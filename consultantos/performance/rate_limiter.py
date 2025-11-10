"""
Adaptive rate limiter with token bucket algorithm.
"""
import asyncio
import time
import logging
from typing import Optional
from collections import deque, defaultdict

logger = logging.getLogger(__name__)


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter using token bucket algorithm.

    Supports:
    - Per-agent rate limiting
    - Burst capacity
    - Adaptive rate adjustment based on errors
    - Priority queuing
    """

    def __init__(
        self,
        rate: float = 10.0,  # tokens per second
        burst: int = 20,  # max burst capacity
        adaptive: bool = True
    ):
        """
        Initialize rate limiter.

        Args:
            rate: Token generation rate (tokens/second)
            burst: Maximum burst capacity
            adaptive: Enable adaptive rate adjustment
        """
        self.base_rate = rate
        self.current_rate = rate
        self.burst = burst
        self.adaptive = adaptive

        # Token bucket
        self.tokens = float(burst)
        self.last_update = time.time()

        # Per-key rate limiting
        self.key_buckets = defaultdict(lambda: {
            'tokens': float(burst),
            'last_update': time.time()
        })

        # Adaptive adjustment tracking
        self.error_count = 0
        self.success_count = 0
        self.last_adjustment = time.time()
        self.adjustment_window = 60.0  # 1 minute

        # Queue for waiting requests
        self.waiting_queue = deque()
        self.lock = asyncio.Lock()

        logger.info(f"Rate limiter initialized: {rate} tokens/s, burst={burst}")

    async def acquire(
        self,
        tokens: int = 1,
        key: Optional[str] = None,
        priority: int = 0
    ) -> bool:
        """
        Acquire tokens from rate limiter.

        Args:
            tokens: Number of tokens to acquire
            key: Optional key for per-resource limiting
            priority: Request priority (higher = more important)

        Returns:
            True if tokens acquired, False if would need to wait too long
        """
        async with self.lock:
            # Update token bucket
            self._update_bucket(key)

            # Check if we have enough tokens
            bucket = self._get_bucket(key)

            if bucket['tokens'] >= tokens:
                # Acquire tokens
                bucket['tokens'] -= tokens
                return True

            # Would need to wait - add to queue
            wait_time = (tokens - bucket['tokens']) / self.current_rate

            if wait_time > 10.0:  # Don't wait more than 10 seconds
                logger.warning(f"Rate limit would require {wait_time:.2f}s wait, rejecting")
                return False

            # Wait for tokens to regenerate
            await asyncio.sleep(wait_time)

            # Try again
            self._update_bucket(key)
            bucket = self._get_bucket(key)

            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                return True

            return False

    async def acquire_nowait(
        self,
        tokens: int = 1,
        key: Optional[str] = None
    ) -> bool:
        """
        Try to acquire tokens without waiting.

        Args:
            tokens: Number of tokens to acquire
            key: Optional key for per-resource limiting

        Returns:
            True if tokens acquired immediately, False otherwise
        """
        async with self.lock:
            self._update_bucket(key)
            bucket = self._get_bucket(key)

            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                return True

            return False

    def _update_bucket(self, key: Optional[str] = None):
        """
        Update token bucket based on time elapsed.

        Args:
            key: Optional key for per-resource bucket
        """
        bucket = self._get_bucket(key)
        now = time.time()
        elapsed = now - bucket['last_update']

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.current_rate
        bucket['tokens'] = min(self.burst, bucket['tokens'] + tokens_to_add)
        bucket['last_update'] = now

    def _get_bucket(self, key: Optional[str] = None) -> dict:
        """
        Get token bucket for key.

        Args:
            key: Optional key for per-resource bucket

        Returns:
            Bucket dict with 'tokens' and 'last_update'
        """
        if key is None:
            return {
                'tokens': self.tokens,
                'last_update': self.last_update
            }
        return self.key_buckets[key]

    def record_success(self):
        """Record successful request for adaptive rate adjustment."""
        if not self.adaptive:
            return

        self.success_count += 1
        self._maybe_adjust_rate()

    def record_error(self):
        """Record failed request for adaptive rate adjustment."""
        if not self.adaptive:
            return

        self.error_count += 1
        self._maybe_adjust_rate()

    def _maybe_adjust_rate(self):
        """Adjust rate based on error rate if window elapsed."""
        now = time.time()

        if now - self.last_adjustment < self.adjustment_window:
            return  # Not time to adjust yet

        total_requests = self.success_count + self.error_count

        if total_requests == 0:
            return  # No data to adjust on

        error_rate = self.error_count / total_requests

        # Adjust rate based on error rate
        if error_rate > 0.1:  # More than 10% errors
            # Decrease rate by 20%
            new_rate = self.current_rate * 0.8
            logger.warning(
                f"High error rate ({error_rate:.1%}), "
                f"decreasing rate to {new_rate:.2f} tokens/s"
            )
            self.current_rate = max(1.0, new_rate)  # Don't go below 1/s

        elif error_rate < 0.01 and self.current_rate < self.base_rate:
            # Less than 1% errors and we're below base rate
            # Increase rate by 10%
            new_rate = min(self.base_rate, self.current_rate * 1.1)
            logger.info(
                f"Low error rate ({error_rate:.1%}), "
                f"increasing rate to {new_rate:.2f} tokens/s"
            )
            self.current_rate = new_rate

        # Reset counters
        self.error_count = 0
        self.success_count = 0
        self.last_adjustment = now

    def get_stats(self) -> dict:
        """Get rate limiter statistics."""
        return {
            "current_rate": self.current_rate,
            "base_rate": self.base_rate,
            "burst_capacity": self.burst,
            "available_tokens": self._get_bucket(None)['tokens'],
            "error_count": self.error_count,
            "success_count": self.success_count,
            "adaptive_enabled": self.adaptive,
            "active_keys": len(self.key_buckets)
        }

    async def reset(self):
        """Reset rate limiter to initial state."""
        async with self.lock:
            self.tokens = float(self.burst)
            self.last_update = time.time()
            self.current_rate = self.base_rate
            self.error_count = 0
            self.success_count = 0
            self.key_buckets.clear()
            logger.info("Rate limiter reset")


class ConcurrencyLimiter:
    """
    Limit concurrent operations with semaphore.
    """

    def __init__(self, max_concurrent: int = 5):
        """
        Initialize concurrency limiter.

        Args:
            max_concurrent: Maximum concurrent operations
        """
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.max_concurrent = max_concurrent
        self.active_count = 0
        self.lock = asyncio.Lock()

        logger.info(f"Concurrency limiter initialized: max={max_concurrent}")

    async def acquire(self):
        """Acquire semaphore slot."""
        await self.semaphore.acquire()
        async with self.lock:
            self.active_count += 1

    def release(self):
        """Release semaphore slot."""
        self.semaphore.release()
        asyncio.create_task(self._decrement_count())

    async def _decrement_count(self):
        """Decrement active count."""
        async with self.lock:
            self.active_count -= 1

    async def __aenter__(self):
        """Context manager entry."""
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()

    def get_stats(self) -> dict:
        """Get concurrency statistics."""
        return {
            "max_concurrent": self.max_concurrent,
            "active_count": self.active_count,
            "available": self.max_concurrent - self.active_count
        }
