"""
Multi-level cache manager with L1 (memory), L2 (Redis), and L3 (disk) caching.
"""
import asyncio
import logging
import pickle
from typing import Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta

try:
    from aiocache import Cache as AioCache
    from aiocache.serializers import PickleSerializer
    AIOCACHE_AVAILABLE = True
except ImportError:
    AIOCACHE_AVAILABLE = False

try:
    import diskcache
    DISKCACHE_AVAILABLE = True
except ImportError:
    DISKCACHE_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Multi-level cache manager with automatic fallback.

    L1: In-memory LRU cache (fast, limited size ~100MB)
    L2: Redis cache (persistent, larger ~1GB)
    L3: Disk cache (persistent, very large ~10GB)
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        disk_path: str = "/tmp/consultantos_cache"
    ):
        """
        Initialize multi-level cache.

        Args:
            redis_url: Redis connection URL (optional)
            disk_path: Path for disk cache storage
        """
        self.stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "misses": 0,
            "errors": 0
        }

        # L1: Memory cache (always available)
        if AIOCACHE_AVAILABLE:
            self.l1_cache = AioCache(
                AioCache.MEMORY,
                serializer=PickleSerializer(),
                ttl=300  # 5 minutes
            )
            logger.info("L1 (memory) cache initialized")
        else:
            self.l1_cache = None
            logger.warning("aiocache not available, L1 cache disabled")

        # L2: Redis cache (optional)
        if AIOCACHE_AVAILABLE and redis_url:
            try:
                self.l2_cache = AioCache(
                    AioCache.REDIS,
                    endpoint=redis_url.split("://")[1].split(":")[0],
                    port=int(redis_url.split(":")[-1]),
                    serializer=PickleSerializer(),
                    ttl=3600  # 1 hour
                )
                logger.info(f"L2 (Redis) cache initialized: {redis_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")
                self.l2_cache = None
        else:
            self.l2_cache = None
            if redis_url:
                logger.warning("aiocache not available, L2 cache disabled")

        # L3: Disk cache (persistent)
        if DISKCACHE_AVAILABLE:
            try:
                self.l3_cache = diskcache.Cache(
                    disk_path,
                    size_limit=int(10e9)  # 10GB
                )
                logger.info(f"L3 (disk) cache initialized: {disk_path}")
            except Exception as e:
                logger.warning(f"Failed to initialize disk cache: {e}")
                self.l3_cache = None
        else:
            self.l3_cache = None
            logger.warning("diskcache not available, L3 cache disabled")

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (checks L1 -> L2 -> L3).

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            # Try L1 (memory)
            if self.l1_cache:
                value = await self.l1_cache.get(key)
                if value is not None:
                    self.stats["l1_hits"] += 1
                    logger.debug(f"L1 cache hit: {key}")
                    return value

            # Try L2 (Redis)
            if self.l2_cache:
                value = await self.l2_cache.get(key)
                if value is not None:
                    self.stats["l2_hits"] += 1
                    logger.debug(f"L2 cache hit: {key}")
                    # Populate L1
                    if self.l1_cache:
                        await self.l1_cache.set(key, value, ttl=300)
                    return value

            # Try L3 (disk)
            if self.l3_cache:
                value = self.l3_cache.get(key)
                if value is not None:
                    self.stats["l3_hits"] += 1
                    logger.debug(f"L3 cache hit: {key}")
                    # Populate L2 and L1
                    if self.l2_cache:
                        await self.l2_cache.set(key, value, ttl=3600)
                    if self.l1_cache:
                        await self.l1_cache.set(key, value, ttl=300)
                    return value

            # Cache miss
            self.stats["misses"] += 1
            logger.debug(f"Cache miss: {key}")
            return None

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ):
        """
        Set value in all cache levels.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)
        """
        try:
            # Store in L1 (memory)
            if self.l1_cache:
                await self.l1_cache.set(
                    key,
                    value,
                    ttl=min(ttl or 300, 300)  # Max 5 minutes in memory
                )

            # Store in L2 (Redis)
            if self.l2_cache:
                await self.l2_cache.set(
                    key,
                    value,
                    ttl=min(ttl or 3600, 3600)  # Max 1 hour in Redis
                )

            # Store in L3 (disk)
            if self.l3_cache:
                self.l3_cache.set(
                    key,
                    value,
                    expire=ttl or 86400  # Default 24 hours on disk
                )

            logger.debug(f"Cached value: {key} (TTL: {ttl}s)")

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"Cache set error for key {key}: {e}")

    async def delete(self, key: str):
        """Delete key from all cache levels."""
        try:
            if self.l1_cache:
                await self.l1_cache.delete(key)
            if self.l2_cache:
                await self.l2_cache.delete(key)
            if self.l3_cache:
                self.l3_cache.delete(key)
            logger.debug(f"Deleted from cache: {key}")
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")

    async def clear(self, pattern: Optional[str] = None):
        """
        Clear cache entries.

        Args:
            pattern: Optional pattern to match (if None, clears all)
        """
        try:
            if pattern:
                # Clear matching entries (L3 only supports pattern matching)
                if self.l3_cache:
                    keys_to_delete = [
                        k for k in self.l3_cache if pattern in str(k)
                    ]
                    for key in keys_to_delete:
                        await self.delete(key)
                    logger.info(f"Cleared {len(keys_to_delete)} entries matching '{pattern}'")
            else:
                # Clear all
                if self.l1_cache:
                    await self.l1_cache.clear()
                if self.l2_cache:
                    await self.l2_cache.clear()
                if self.l3_cache:
                    self.l3_cache.clear()
                logger.info("Cleared all cache entries")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

    async def get_or_compute(
        self,
        key: str,
        compute_fn: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Get from cache or compute if missing.

        Args:
            key: Cache key
            compute_fn: Async function to compute value if not cached
            ttl: Time to live in seconds

        Returns:
            Cached or computed value
        """
        # Try cache first
        value = await self.get(key)
        if value is not None:
            return value

        # Compute value
        if asyncio.iscoroutinefunction(compute_fn):
            value = await compute_fn()
        else:
            value = compute_fn()

        # Store in cache
        await self.set(key, value, ttl=ttl)

        return value

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total_requests = sum([
            self.stats["l1_hits"],
            self.stats["l2_hits"],
            self.stats["l3_hits"],
            self.stats["misses"]
        ])

        hit_rate = 0.0
        if total_requests > 0:
            total_hits = (
                self.stats["l1_hits"] +
                self.stats["l2_hits"] +
                self.stats["l3_hits"]
            )
            hit_rate = total_hits / total_requests

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "l1_available": self.l1_cache is not None,
            "l2_available": self.l2_cache is not None,
            "l3_available": self.l3_cache is not None
        }


def cached(
    key_fn: Callable,
    ttl: int = 3600
):
    """
    Decorator for caching function results.

    Args:
        key_fn: Function to generate cache key from args
        ttl: Time to live in seconds

    Example:
        @cached(lambda company, industry: f"analysis:{company}:{industry}", ttl=3600)
        async def analyze(company: str, industry: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = key_fn(*args, **kwargs)

            # Get cache manager (assumes it's injected or global)
            # For now, create a new instance
            cache = CacheManager()

            # Try cache first
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # Compute
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Store
            await cache.set(cache_key, result, ttl=ttl)

            return result
        return wrapper
    return decorator
