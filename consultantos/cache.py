"""
Multi-level caching system for ConsultantOS
"""
import hashlib
import json
import logging
from typing import Any, Optional, List, Dict
from functools import wraps
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
            # Double-checked locking pattern
            if _disk_cache is None:
                cache_dir = "/tmp/consultantos_cache"
                _disk_cache = diskcache.Cache(cache_dir, size_limit=int(1e9))  # 1GB
                logger.info(f"Initialized disk cache at {cache_dir}")
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
            # Double-checked locking pattern
            if _chroma_client is None:
                try:
                    _chroma_client = chromadb.Client(Settings(
                        chroma_db_impl="duckdb+parquet",
                        persist_directory="/tmp/consultantos_chroma"
                    ))
                    _chroma_collection = _chroma_client.get_or_create_collection(
                        name="analysis_cache",
                        metadata={"description": "Semantic cache for analysis results"}
                    )
                    logger.info("Initialized ChromaDB semantic cache")
                except Exception as e:
                    logger.warning(f"Failed to initialize ChromaDB: {e}. Semantic caching disabled.")
                    _chroma_collection = None
    return _chroma_collection


def cache_key(company: str, frameworks: List[str], industry: Optional[str] = None) -> str:
    """Generate cache key from request parameters"""
    key_parts = [company.lower().strip()]
    if industry:
        key_parts.append(industry.lower().strip())
    key_parts.extend(sorted([f.lower().strip() for f in frameworks]))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached_analysis(cache_key_str: str, ttl: Optional[int] = None):
    """
    Decorator for caching analysis results
    
    Args:
        cache_key_str: Cache key string
        ttl: Time to live in seconds (defaults to settings.cache_ttl_seconds)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Check disk cache first (with error handling)
            disk = get_disk_cache()
            if disk is not None:
                try:
                    cached_result = disk.get(cache_key_str)
                    if cached_result is not None:
                        logger.info(f"Cache hit (disk): {cache_key_str}")
                        return cached_result
                except Exception as e:
                    logger.warning(f"Cache get failed for key {cache_key_str}: {e}", exc_info=True)
                    # Treat as cache miss and continue
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in disk cache (with error handling)
            if disk is not None:
                try:
                    ttl_seconds = ttl or settings.cache_ttl_seconds
                    disk.set(cache_key_str, result, expire=ttl_seconds)
                    logger.info(f"Cached result (disk): {cache_key_str} (TTL: {ttl_seconds}s)")
                except Exception as e:
                    logger.warning(f"Cache set failed for key {cache_key_str} (TTL: {ttl_seconds}s): {e}", exc_info=True)
                    # Silently ignore caching errors - function result still returned
            
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
        # Create query text
        query_text = f"{company} {' '.join(frameworks)}"
        
        # Search for similar queries
        results = collection.query(
            query_texts=[query_text],
            n_results=1
        )
        
        if results and len(results['ids']) > 0 and len(results['ids'][0]) > 0:
            # Check similarity (ChromaDB returns distances, lower is more similar)
            distance = results['distances'][0][0] if results['distances'] else 1.0
            similarity = 1.0 - distance
            
            if similarity >= threshold:
                # Retrieve cached result
                cached_id = results['ids'][0][0]
                cached_data = collection.get(ids=[cached_id])
                
                if cached_data and 'metadatas' in cached_data and cached_data['metadatas']:
                    cache_key_str = cached_data['metadatas'][0].get('cache_key')
                    if cache_key_str:
                        disk = get_disk_cache()
                        result = disk.get(cache_key_str)
                        if result:
                            logger.info(
                                f"Cache hit (semantic): {company} "
                                f"(similarity: {similarity:.2f})"
                            )
                            return result
        
        return None
    except Exception as e:
        logger.warning(f"Semantic cache lookup failed: {e}")
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
        # Create document text for semantic search
        doc_text = f"{company} {' '.join(frameworks)}"
        
        # Store in ChromaDB
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


def clear_cache(pattern: Optional[str] = None):
    """
    Clear cache entries
    
    Args:
        pattern: Optional pattern to match (if None, clears all)
    """
    disk = get_disk_cache()
    if disk is not None:
        if pattern:
            # Clear matching entries
            try:
                keys_to_delete = [k for k in disk if pattern in str(k)]
                for key in keys_to_delete:
                    disk.delete(key)
                logger.info(f"Cleared {len(keys_to_delete)} cache entries matching '{pattern}'")
            except Exception as e:
                logger.warning(f"Failed to clear cache entries matching '{pattern}': {e}")
        else:
            # Clear all
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
            collection.delete()  # Delete collection
            # Recreate
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
    
    # This would trigger async analysis for each company/framework combination
    # For now, just log - actual implementation would queue background jobs
    for company in companies:
        for framework_set in [frameworks[:2], frameworks]:
            cache_key_str = cache_key(company, framework_set)
            disk = get_disk_cache()
            if disk and not disk.get(cache_key_str):
                logger.debug(f"Cache miss for {company} with {framework_set} - would warm")
    
    logger.info("Cache warming complete")


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics
    
    Returns:
        Dictionary with cache statistics
    """
    stats = {
        "disk_cache": {
            "available": False,
            "size": 0,
            "entries": 0
        },
        "semantic_cache": {
            "available": False,
            "entries": 0
        }
    }
    
    disk = get_disk_cache()
    if disk:
        stats["disk_cache"]["available"] = True
        stats["disk_cache"]["size"] = disk.volume()
        stats["disk_cache"]["entries"] = len(disk)
    
    collection = get_chroma_collection()
    if collection:
        stats["semantic_cache"]["available"] = True
        # Get count (approximate)
        try:
            results = collection.get()
            stats["semantic_cache"]["entries"] = len(results.get("ids", [])) if results else 0
        except Exception:
            pass
    
    return stats

