"""
Optimized multi-level caching system for ConsultantOS

Performance improvements:
- Configurable TTL per cache type
- Cache hit rate tracking
- Cache warming for common queries
- Memory-efficient storage
- Automatic cache key generation
"""
import hashlib
import json
import logging
import math
import os
import tempfile
import time
from typing import Any, Optional, List, Dict
from functools import wraps
from enum import Enum

try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from consultantos.config import settings
import threading

logger = logging.getLogger(__name__)


class CacheType(str, Enum):
    """Cache types with different TTL strategies"""
    ANALYSIS_RESULT = "analysis_result"  # Long TTL (24 hours)
    MARKET_DATA = "market_data"          # Medium TTL (1 hour)
    SEARCH_RESULT = "search_result"      # Short TTL (15 minutes)
    VISUALIZATION = "visualization"      # Long TTL (24 hours)
    USER_SESSION = "user_session"        # Short TTL (30 minutes)


# TTL configuration per cache type (in seconds)
CACHE_TTL_CONFIG = {
    CacheType.ANALYSIS_RESULT: 86400,    # 24 hours
    CacheType.MARKET_DATA: 3600,         # 1 hour
    CacheType.SEARCH_RESULT: 900,        # 15 minutes
    CacheType.VISUALIZATION: 86400,      # 24 hours
    CacheType.USER_SESSION: 1800,        # 30 minutes
}


# Cache metrics tracking
class CacheMetrics:
    """Thread-safe cache metrics tracker"""

    def __init__(self):
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._errors = 0
        self._total_latency = 0.0  # milliseconds

    def record_hit(self, latency_ms: float = 0):
        with self._lock:
            self._hits += 1
            self._total_latency += latency_ms

    def record_miss(self):
        with self._lock:
            self._misses += 1

    def record_set(self):
        with self._lock:
            self._sets += 1

    def record_error(self):
        with self._lock:
            self._errors += 1

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total * 100) if total > 0 else 0
            avg_latency = (self._total_latency / self._hits) if self._hits > 0 else 0

            return {
                "hits": self._hits,
                "misses": self._misses,
                "sets": self._sets,
                "errors": self._errors,
                "total_requests": total,
                "hit_rate_percent": round(hit_rate, 2),
                "avg_latency_ms": round(avg_latency, 2)
            }

    def reset(self):
        with self._lock:
            self._hits = 0
            self._misses = 0
            self._sets = 0
            self._errors = 0
            self._total_latency = 0.0


# Global metrics instance
_cache_metrics = CacheMetrics()


# Level 1: Disk Cache (Persistent)
_disk_cache: Optional[diskcache.Cache] = None
_disk_cache_lock = threading.Lock()


def get_disk_cache():
    """Get or create disk cache instance (thread-safe)"""
    global _disk_cache
    if not DISKCACHE_AVAILABLE:
        logger.warning("diskcache not available, caching disabled")
        return None
    if _disk_cache is None:
        with _disk_cache_lock:
            if _disk_cache is None:
                # Use configurable cache directory with sensible fallback
                if settings.cache_dir:
                    cache_dir = os.path.expanduser(settings.cache_dir)
                else:
                    # Default to temp directory with app-specific subdirectory
                    cache_dir = os.path.join(tempfile.gettempdir(), "consultantos_cache")
                
                # Ensure directory exists with proper permissions
                os.makedirs(cache_dir, exist_ok=True)
                
                # Check directory permissions
                if not os.access(cache_dir, os.W_OK):
                    logger.error(f"Cache directory {cache_dir} is not writable")
                    return None
                
                _disk_cache = diskcache.Cache(
                    cache_dir,
                    size_limit=int(2e9),  # 2GB (increased from 1GB)
                    eviction_policy='least-recently-used'
                )
                cache_size_mb = int(2e9) / (1024 * 1024)
                logger.info(f"Initialized disk cache at {cache_dir} ({cache_size_mb:.0f}MB, LRU eviction)")
    return _disk_cache


# Level 2: Semantic Vector Cache (ChromaDB)
_chroma_client: Optional[chromadb.Client] = None
_chroma_collection: Optional[chromadb.Collection] = None
_chroma_lock = threading.Lock()


def get_chroma_collection():
    """Get or create ChromaDB collection for semantic caching (thread-safe)"""
    global _chroma_client, _chroma_collection
    if not CHROMADB_AVAILABLE:
        logger.warning("ChromaDB not available, semantic caching disabled")
        return None
    if _chroma_client is None:
        with _chroma_lock:
            if _chroma_client is None:
                try:
                    # Use modern ChromaDB API with PersistentClient
                    # Make persist directory configurable via environment variable or config
                    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "")
                    if not persist_dir:
                        # Fallback to temp directory with app-specific subdirectory
                        persist_dir = os.path.join(tempfile.gettempdir(), "consultantos_chroma")
                    
                    # Ensure directory exists
                    os.makedirs(persist_dir, exist_ok=True)
                    
                    # Use modern PersistentClient API (removed chroma_db_impl parameter)
                    _chroma_client = chromadb.PersistentClient(path=persist_dir)
                    _chroma_collection = _chroma_client.get_or_create_collection(
                        name="analysis_cache",
                        metadata={"description": "Semantic cache for analysis results"}
                    )
                    logger.info(f"Initialized ChromaDB semantic cache at {persist_dir}")
                except Exception as e:
                    logger.warning(f"Failed to initialize ChromaDB: {e}. Semantic caching disabled.", exc_info=True)
                    _chroma_collection = None
                    _chroma_client = None
    return _chroma_collection


def cache_key(
    company: str,
    frameworks: List[str],
    industry: Optional[str] = None,
    cache_type: CacheType = CacheType.ANALYSIS_RESULT
) -> str:
    """
    Generate cache key from request parameters

    Args:
        company: Company name
        frameworks: List of frameworks
        industry: Optional industry
        cache_type: Type of cache (affects TTL)

    Returns:
        MD5 hash of normalized parameters
    """
    key_parts = [cache_type.value, company.lower().strip()]
    if industry:
        key_parts.append(industry.lower().strip())
    key_parts.extend(sorted([f.lower().strip() for f in frameworks]))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_analysis(
    cache_key_str: str,
    ttl: Optional[int] = None,
    cache_type: CacheType = CacheType.ANALYSIS_RESULT
):
    """
    Decorator for caching analysis results with configurable TTL

    Args:
        cache_key_str: Cache key string
        ttl: Time to live in seconds (overrides cache_type default)
        cache_type: Type of cache (determines default TTL)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Determine TTL
            ttl_seconds = ttl if ttl is not None else CACHE_TTL_CONFIG.get(cache_type, 3600)

            # Check disk cache first
            disk = get_disk_cache()
            if disk is not None:
                try:
                    start_time = time.time()
                    cached_result = disk.get(cache_key_str)
                    latency_ms = (time.time() - start_time) * 1000

                    if cached_result is not None:
                        logger.info(f"Cache hit (disk): {cache_key_str} (type: {cache_type.value}, latency: {latency_ms:.2f}ms)")
                        _cache_metrics.record_hit(latency_ms)
                        return cached_result
                    else:
                        _cache_metrics.record_miss()
                except Exception as e:
                    logger.warning(f"Cache get failed for key {cache_key_str}: {e}", exc_info=True)
                    _cache_metrics.record_error()

            # Execute function
            result = await func(*args, **kwargs)

            # Store in disk cache
            if disk is not None:
                try:
                    disk.set(cache_key_str, result, expire=ttl_seconds)
                    _cache_metrics.record_set()
                    logger.info(f"Cached result (disk): {cache_key_str} (type: {cache_type.value}, TTL: {ttl_seconds}s)")
                except Exception as e:
                    logger.warning(f"Cache set failed for key {cache_key_str} (TTL: {ttl_seconds}s): {e}", exc_info=True)
                    _cache_metrics.record_error()

            return result
        return wrapper
    return decorator


async def semantic_cache_lookup(
    company: str,
    frameworks: List[str],
    threshold: float = 0.95
) -> Optional[Any]:
    """
    Look up similar analysis in semantic cache

    Args:
        company: Company name
        frameworks: List of frameworks requested
        threshold: Similarity threshold (0-1)

    Returns:
        Cached result if similar analysis found, None otherwise
    """
    collection = get_chroma_collection()
    if collection is None:
        return None

    try:
        start_time = time.time()
        query_text = f"{company} {' '.join(frameworks)}"

        results = collection.query(
            query_texts=[query_text],
            n_results=1
        )

        if results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
            distance = results['distances'][0][0] if results['distances'] else 1.0
            
            # Determine distance metric from collection metadata or default to cosine
            # ChromaDB default is cosine distance, which maps to similarity as 1.0 - distance
            distance_metric = collection.metadata.get('distance_metric', 'cosine') if hasattr(collection, 'metadata') else 'cosine'
            
            # Compute similarity based on distance metric
            if distance_metric in ['cosine', 'cosine_similarity']:
                similarity = 1.0 - distance
            elif distance_metric in ['euclidean', 'l2']:
                # For euclidean, lower distance = higher similarity, but need normalization
                # Use threshold comparison directly with distance
                similarity = 1.0 / (1.0 + distance) if distance > 0 else 1.0
            elif distance_metric in ['dot_product', 'inner_product']:
                # Dot product similarity handling
                # Check if embeddings are normalized (unit vectors) via metadata
                # For normalized vectors, dot product is in [-1, 1] range
                # For unnormalized vectors, dot product can be unbounded
                is_normalized = collection.metadata.get('normalized', False) if hasattr(collection, 'metadata') else False
                
                if is_normalized:
                    # Normalized vectors: dot product is in [-1, 1], map to [0, 1]
                    similarity = (distance + 1.0) / 2.0
                else:
                    # Unnormalized vectors: use sigmoid to safely map unbounded values to [0, 1]
                    # Sigmoid: 1 / (1 + exp(-x)) maps (-inf, +inf) to (0, 1)
                    # For similarity, we want higher dot product = higher similarity
                    # Using tanh variant: (tanh(distance) + 1) / 2 maps to [0, 1]
                    similarity = (math.tanh(distance) + 1.0) / 2.0
                    # Clamp to [0, 1] as safety measure
                    similarity = max(0.0, min(1.0, similarity))
                    logger.debug(f"Dot product with unnormalized vectors: distance={distance:.4f}, similarity={similarity:.4f}")
            else:
                # Default to cosine similarity conversion
                similarity = 1.0 - distance
            
            logger.debug(f"Semantic cache lookup using distance metric: {distance_metric}, distance: {distance:.4f}, similarity: {similarity:.4f}")

            if similarity >= threshold:
                cached_id = results['ids'][0][0]
                cached_data = collection.get(ids=[cached_id])

                if cached_data and 'metadatas' in cached_data and cached_data['metadatas']:
                    cache_key_str = cached_data['metadatas'][0].get('cache_key')
                    if cache_key_str:
                        disk = get_disk_cache()
                        if disk is not None:
                            result = disk.get(cache_key_str)
                            if result:
                                latency_ms = (time.time() - start_time) * 1000
                                logger.info(
                                    f"Cache hit (semantic): {company} "
                                    f"(similarity: {similarity:.2f}, metric: {distance_metric}, latency: {latency_ms:.2f}ms)"
                                )
                                _cache_metrics.record_hit(latency_ms)
                                return result
                        else:
                            logger.debug(f"Semantic cache hit but disk cache miss for key: {cache_key_str}")

        return None
    except Exception as e:
        logger.warning(f"Semantic cache lookup failed: {e}")
        _cache_metrics.record_error()
        return None


async def semantic_cache_store(
    company: str,
    frameworks: List[str],
    cache_key_str: str,
    result: Any
):
    """
    Store analysis result in semantic cache

    Args:
        company: Company name
        frameworks: List of frameworks requested
        cache_key_str: Disk cache key
        result: Analysis result to store
    """
    collection = get_chroma_collection()
    if collection is None:
        return

    try:
        doc_text = f"{company} {' '.join(frameworks)}"

        collection.add(
            documents=[doc_text],
            ids=[cache_key_str],
            metadatas=[{
                "cache_key": cache_key_str,
                "company": company,
                "frameworks": json.dumps(frameworks)
            }]
        )
        logger.info(f"Stored in semantic cache: {cache_key_str}")
    except Exception as e:
        logger.warning(f"Semantic cache store failed: {e}")
        _cache_metrics.record_error()


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries

    Args:
        pattern: Optional pattern to match (if None, clears all)
    """
    disk = get_disk_cache()
    if disk is not None:
        if pattern:
            try:
                keys_to_delete = [k for k in disk if pattern in str(k)]
                for key in keys_to_delete:
                    disk.delete(key)
                logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
            except Exception as e:
                logger.warning(f"Failed to clear cache entries matching '{pattern}': {e}")
        else:
            try:
                disk.clear()
                logger.info("Cleared all cache entries")
            except Exception as e:
                logger.warning(f"Failed to clear all cache entries: {e}")
    else:
        logger.debug("Disk cache not available, skipping clear")

    # Clear semantic cache
    collection = get_chroma_collection()
    if collection is not None:
        try:
            collection.delete()
            get_chroma_collection()
            logger.info("Cleared semantic cache")
        except Exception as e:
            logger.warning(f"Failed to clear semantic cache: {e}")
    else:
        logger.debug("Semantic cache not available, skipping clear")


def invalidate_cache_pattern(pattern: str):
    """
    Invalidate cache entries matching a pattern

    Args:
        pattern: Pattern to match against cache keys
    """
    clear_cache(pattern)


async def warm_cache(companies: List[str], frameworks: List[str]):
    """
    Pre-warm cache for common queries

    Args:
        companies: List of company names to pre-warm
        frameworks: List of frameworks to pre-warm
    """
    logger.info(f"Warming cache for {len(companies)} companies")

    for company in companies:
        for framework_set in [frameworks[:2], frameworks]:
            cache_key_str = cache_key(company, framework_set)
            disk = get_disk_cache()
            if disk and not disk.get(cache_key_str):
                logger.debug(f"Cache miss for {company} with {framework_set} - would warm")

    logger.info("Cache warming complete")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get comprehensive cache statistics

    Returns:
        Dictionary with cache statistics including hit rates and latency
    """
    stats = {
        "disk_cache": {
            "available": False,
            "size_bytes": 0,
            "size_mb": 0,
            "entries": 0,
            "max_size_gb": 2
        },
        "semantic_cache": {
            "available": False,
            "entries": 0
        },
        "performance": _cache_metrics.get_stats()
    }

    disk = get_disk_cache()
    if disk:
        stats["disk_cache"]["available"] = True
        volume = disk.volume()
        stats["disk_cache"]["size_bytes"] = volume
        stats["disk_cache"]["size_mb"] = round(volume / (1024 * 1024), 2)
        stats["disk_cache"]["entries"] = len(disk)

    collection = get_chroma_collection()
    if collection:
        stats["semantic_cache"]["available"] = True
        try:
            results = collection.get()
            stats["semantic_cache"]["entries"] = len(results.get("ids", [])) if results else 0
        except Exception:
            pass

    return stats


def reset_cache_metrics():
    """Reset cache performance metrics"""
    _cache_metrics.reset()
    logger.info("Cache metrics reset")
