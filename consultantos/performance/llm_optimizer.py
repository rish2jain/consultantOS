"""
LLM call optimization with batching, caching, and rate limiting.
"""
import asyncio
import logging
import hashlib
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

from consultantos.performance.cache_manager import CacheManager
from consultantos.performance.rate_limiter import AdaptiveRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class LLMRequest:
    """LLM request with metadata."""
    prompt: str
    model: str
    agent_name: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    cache_ttl: int = 3600


@dataclass
class LLMResponse:
    """LLM response with metadata."""
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    duration: float
    cached: bool = False


class LLMOptimizer:
    """
    Optimized LLM client with batching, caching, and rate limiting.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_manager: Optional[CacheManager] = None,
        rate_limiter: Optional[AdaptiveRateLimiter] = None,
        max_batch_size: int = 5,
        batch_window: float = 0.1  # 100ms batching window
    ):
        """
        Initialize LLM optimizer.

        Args:
            api_key: Gemini API key
            cache_manager: Cache manager instance
            rate_limiter: Rate limiter instance
            max_batch_size: Maximum requests per batch
            batch_window: Time window for batching requests (seconds)
        """
        if not GENAI_AVAILABLE:
            logger.warning("Google Generative AI not available")
            self.client = None
        else:
            if api_key:
                genai.configure(api_key=api_key)
            self.client = genai

        self.cache = cache_manager or CacheManager()
        self.rate_limiter = rate_limiter or AdaptiveRateLimiter(rate=10.0)

        self.max_batch_size = max_batch_size
        self.batch_window = batch_window

        # Batch queue
        self._batch_queue: List[tuple] = []  # (request, future)
        self._batch_lock = asyncio.Lock()
        self._batch_timer = None

        # Stats
        self.stats = {
            "total_requests": 0,
            "cached_requests": 0,
            "batched_requests": 0,
            "rate_limited_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_duration": 0.0
        }

        logger.info(
            f"LLM optimizer initialized: batch_size={max_batch_size}, "
            f"window={batch_window}s"
        )

    async def generate(
        self,
        request: LLMRequest,
        use_cache: bool = True,
        use_batching: bool = False
    ) -> LLMResponse:
        """
        Generate response from LLM with optimization.

        Args:
            request: LLM request
            use_cache: Whether to use semantic cache
            use_batching: Whether to batch this request

        Returns:
            LLM response with metadata
        """
        self.stats["total_requests"] += 1

        # Check cache first
        if use_cache:
            cache_key = self._generate_cache_key(request)
            cached_response = await self.cache.get(cache_key)

            if cached_response:
                self.stats["cached_requests"] += 1
                logger.debug(f"Cache hit for {request.agent_name}")
                return LLMResponse(
                    text=cached_response["text"],
                    model=request.model,
                    input_tokens=cached_response.get("input_tokens", 0),
                    output_tokens=cached_response.get("output_tokens", 0),
                    duration=0.0,
                    cached=True
                )

        # Use batching if requested
        if use_batching:
            response = await self._generate_batched(request)
        else:
            response = await self._generate_single(request)

        # Cache response
        if use_cache and response:
            cache_key = self._generate_cache_key(request)
            await self.cache.set(
                cache_key,
                {
                    "text": response.text,
                    "input_tokens": response.input_tokens,
                    "output_tokens": response.output_tokens
                },
                ttl=request.cache_ttl
            )

        return response

    async def _generate_single(self, request: LLMRequest) -> LLMResponse:
        """
        Generate single LLM response.

        Args:
            request: LLM request

        Returns:
            LLM response
        """
        if not self.client:
            raise RuntimeError("Gemini client not available")

        # Rate limiting
        acquired = await self.rate_limiter.acquire(tokens=1, key=request.agent_name)
        if not acquired:
            self.stats["rate_limited_requests"] += 1
            raise RuntimeError("Rate limit exceeded")

        start_time = time.time()

        try:
            # Create model
            model = self.client.GenerativeModel(request.model)

            # Generate
            generation_config = {
                "temperature": request.temperature,
            }
            if request.max_tokens:
                generation_config["max_output_tokens"] = request.max_tokens

            response = model.generate_content(
                request.prompt,
                generation_config=generation_config
            )

            duration = time.time() - start_time

            # Extract tokens (Gemini API provides usage metadata)
            input_tokens = 0
            output_tokens = 0

            if hasattr(response, 'usage_metadata'):
                input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)

            # Update stats
            self.stats["total_input_tokens"] += input_tokens
            self.stats["total_output_tokens"] += output_tokens
            self.stats["total_duration"] += duration

            # Record success
            self.rate_limiter.record_success()

            return LLMResponse(
                text=response.text,
                model=request.model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration=duration
            )

        except Exception as e:
            self.rate_limiter.record_error()
            logger.error(f"LLM generation failed: {e}")
            raise

    async def _generate_batched(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response using batching.

        Args:
            request: LLM request

        Returns:
            LLM response
        """
        # Create future for this request
        future = asyncio.Future()

        async with self._batch_lock:
            # Add to batch queue
            self._batch_queue.append((request, future))

            # Start batch timer if not already running
            if self._batch_timer is None or self._batch_timer.done():
                self._batch_timer = asyncio.create_task(self._process_batch())

            # Check if batch is full
            if len(self._batch_queue) >= self.max_batch_size:
                # Process immediately
                if not self._batch_timer.done():
                    self._batch_timer.cancel()
                asyncio.create_task(self._process_batch())

        # Wait for result
        return await future

    async def _process_batch(self):
        """Process batched requests."""
        # Wait for batching window
        await asyncio.sleep(self.batch_window)

        async with self._batch_lock:
            if not self._batch_queue:
                return

            # Get batch
            batch = self._batch_queue[:self.max_batch_size]
            self._batch_queue = self._batch_queue[self.max_batch_size:]

            logger.info(f"Processing batch of {len(batch)} requests")
            self.stats["batched_requests"] += len(batch)

        # Process batch in parallel (with rate limiting)
        tasks = [
            self._generate_single(req)
            for req, _ in batch
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Set futures
        for (_, future), result in zip(batch, results):
            if isinstance(result, Exception):
                future.set_exception(result)
            else:
                future.set_result(result)

    def _generate_cache_key(self, request: LLMRequest) -> str:
        """
        Generate cache key for request.

        Args:
            request: LLM request

        Returns:
            Cache key string
        """
        # Include model, prompt, and key parameters
        key_parts = [
            request.model,
            request.prompt,
            str(request.temperature),
            str(request.max_tokens or "none")
        ]
        key_string = "|".join(key_parts)
        return f"llm:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def generate_batch(
        self,
        requests: List[LLMRequest],
        use_cache: bool = True
    ) -> List[LLMResponse]:
        """
        Generate responses for multiple requests efficiently.

        Args:
            requests: List of LLM requests
            use_cache: Whether to use cache

        Returns:
            List of LLM responses
        """
        # Process all requests in parallel
        tasks = [
            self.generate(req, use_cache=use_cache, use_batching=False)
            for req in requests
        ]

        return await asyncio.gather(*tasks, return_exceptions=False)

    def get_stats(self) -> Dict[str, Any]:
        """Get LLM optimizer statistics."""
        total_tokens = self.stats["total_input_tokens"] + self.stats["total_output_tokens"]
        cache_rate = 0.0

        if self.stats["total_requests"] > 0:
            cache_rate = self.stats["cached_requests"] / self.stats["total_requests"]

        avg_duration = 0.0
        if self.stats["total_requests"] - self.stats["cached_requests"] > 0:
            avg_duration = self.stats["total_duration"] / (
                self.stats["total_requests"] - self.stats["cached_requests"]
            )

        return {
            **self.stats,
            "total_tokens": total_tokens,
            "cache_hit_rate": cache_rate,
            "average_duration": avg_duration,
            "rate_limiter": self.rate_limiter.get_stats()
        }

    async def warm_cache(self, requests: List[LLMRequest]):
        """
        Pre-warm cache with common requests.

        Args:
            requests: List of requests to pre-warm
        """
        logger.info(f"Warming cache with {len(requests)} requests")

        for request in requests:
            cache_key = self._generate_cache_key(request)
            cached = await self.cache.get(cache_key)

            if not cached:
                # Generate and cache
                await self.generate(request, use_cache=True)

        logger.info("Cache warming complete")
