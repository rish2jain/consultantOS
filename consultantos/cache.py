"""
Multi-level caching system for ConsultantOS
"""
import asyncio
import hashlib
import json
import logging
import os
import tempfile
from typing import Any, Optional, List, Dict
from functools import wraps, partial
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

def _resolve_cache_dir() -> str:
    """Determine the on-disk cache directory respecting settings."""
    configured_dir = (settings.cache_dir or "").strip()
    if configured_dir:
        cache_dir = os.path.expanduser(configured_dir)
    else:
        cache_dir = os.path.join(tempfile.gettempdir(), "consultantos_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


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
                try:
                    cache_dir = _resolve_cache_dir()
                    _disk_cache = diskcache.Cache(cache_dir, size_limit=int(1e9))  # 1GB
                    logger.info(f"Initialized disk cache at {cache_dir}")
                except Exception as e:
                    logger.error(f"Failed to initialize disk cache: {e}")
                    _disk_cache = None
    return _disk_cache

# Level 2: Semantic Vector Cache (ChromaDB)
_chroma_client: Optional[chromadb.Client] = None
_chroma_collection: Optional[chromadb.Collection] = None
_chroma_lock = threading.Lock()

def get_chroma_collection():
    """Get or create ChromaDB collection for semantic caching (thread-safe, non-blocking)"""
    global _chroma_client, _chroma_collection
    if not CHROMADB_AVAILABLE:
        logger.warning("ChromaDB not available, semantic caching disabled")
        return None
    
    # Fast path: already initialized (check for both None and False)
    if _chroma_client is not None and _chroma_client is not False:
        return _chroma_collection
    
    # If initialization previously failed, return None immediately
    if _chroma_client is False:
        return None
    
    # Use non-blocking lock acquisition to prevent deadlocks
    # If lock is held, another thread is initializing - return None gracefully
    lock_acquired = False
    try:
        lock_acquired = _chroma_lock.acquire(blocking=False)
        if not lock_acquired:
            # Another thread is initializing, return None for now
            # The caller should handle None gracefully (semantic cache is optional)
            logger.debug("ChromaDB initialization in progress, skipping this request")
            return None
        
        # Double-checked locking pattern
        if _chroma_client is None:
            try:
                # ChromaDB initialization can block if DuckDB file locks are held
                # Disable telemetry to avoid network calls that might block
                _chroma_client = chromadb.Client(Settings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory="/tmp/consultantos_chroma",
                    anonymized_telemetry=False  # Disable telemetry to avoid blocking
                ))
                _chroma_collection = _chroma_client.get_or_create_collection(
                    name="analysis_cache",
                    metadata={"description": "Semantic cache for analysis results"}
                )
                logger.info("Initialized ChromaDB semantic cache")
            except Exception as e:
                logger.warning(f"Failed to initialize ChromaDB: {e}. Semantic caching disabled.")
                # Mark as failed to avoid repeated attempts
                _chroma_client = False  # Use False to indicate failed init (not None)
                _chroma_collection = None
    finally:
        if lock_acquired:
            _chroma_lock.release()
    
    # Return None if initialization failed (False indicates failed init)
    if _chroma_client is False:
        return None
    
    return _chroma_collection


def cache_key(
    company: str,
    frameworks: List[str],
    industry: Optional[str] = None,
    depth: Optional[str] = None,
) -> str:
    """Generate cache key from request parameters"""
    def _normalize(value: Optional[str]) -> Optional[str]:
        return value.lower().strip() if value else None

    key_parts = [part for part in [
        _normalize(company),
        _normalize(industry),
        _normalize(depth)
    ] if part]
    key_parts.extend(sorted([
        f.lower().strip() for f in frameworks if f and f.strip()
    ]))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


async def store_disk_cache_result(
    cache_key_str: str,
    result: Any,
    ttl: Optional[int] = None,
):
    """Persist result in disk cache so semantic cache can point to it."""
    disk = get_disk_cache()
    if disk is None:
        return
    ttl_seconds = ttl or settings.cache_ttl_seconds
    try:
        await asyncio.to_thread(
            partial(disk.set, cache_key_str, result, expire=ttl_seconds)
        )
        logger.info(
            f"Cached result (disk): {cache_key_str} (TTL: {ttl_seconds}s)"
        )
    except Exception as e:
        logger.warning(
            f"Cache set failed for key {cache_key_str} (TTL: {ttl_seconds}s): {e}",
            exc_info=True,
        )


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
                    cached_result = await asyncio.to_thread(disk.get, cache_key_str)
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
                await store_disk_cache_result(cache_key_str, result, ttl)

            return result
        return wrapper
    return decorator


async def semantic_cache_lookup(
    company: str,
    frameworks: List[str],
    industry: Optional[str] = None,
    depth: Optional[str] = None,
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
        normalized_company = company.lower().strip()
        normalized_industry = industry.lower().strip() if industry else None
        normalized_depth = depth.lower().strip() if depth else None
        framework_signature = " ".join(sorted([f.lower().strip() for f in frameworks]))

        # Create query text that includes contextual dimensions
        context_bits = [normalized_company, normalized_industry, normalized_depth, framework_signature]
        query_text = " | ".join(filter(None, context_bits))
        
        # Search for similar queries
        results = await asyncio.to_thread(
            collection.query,
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
                cached_data = await asyncio.to_thread(
                    collection.get,
                    ids=[cached_id]
                )
                
                if cached_data and 'metadatas' in cached_data and cached_data['metadatas']:
                    metadata = cached_data['metadatas'][0]
                    # Ensure metadata context matches request to avoid cross-company leakage
                    if metadata.get('industry') and normalized_industry and metadata['industry'] != normalized_industry:
                        return None
                    if metadata.get('depth') and normalized_depth and metadata['depth'] != normalized_depth:
                        return None
                    if metadata.get('framework_signature') and metadata['framework_signature'] != framework_signature:
                        return None

                    cache_key_str = metadata.get('cache_key')
                    if cache_key_str:
                        disk = get_disk_cache()
                        result = await asyncio.to_thread(disk.get, cache_key_str) if disk else None
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
    result: Any,
    industry: Optional[str] = None,
    depth: Optional[str] = None,
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
        normalized_company = company.lower().strip()
        normalized_industry = industry.lower().strip() if industry else None
        normalized_depth = depth.lower().strip() if depth else None
        framework_signature = " ".join(sorted([f.lower().strip() for f in frameworks]))

        # Create document text for semantic search
        context_bits = [normalized_company, normalized_industry, normalized_depth, framework_signature]
        doc_text = " | ".join(filter(None, context_bits))

        # Store in ChromaDB
        await asyncio.to_thread(
            collection.add,
            documents=[doc_text],
            ids=[cache_key_str],
            metadatas=[{
                "cache_key": cache_key_str,
                "company": normalized_company,
                "industry": normalized_industry,
                "depth": normalized_depth,
                "framework_signature": framework_signature,
                "frameworks": json.dumps(frameworks)
            }]
        )
        logger.info(f"Stored in semantic cache: {cache_key_str}")
    except Exception as e:
        logger.warning(f"Semantic cache store failed: {e}")
    
    # Ensure disk cache holds the underlying report for subsequent fetches
    await store_disk_cache_result(cache_key_str, result)

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
