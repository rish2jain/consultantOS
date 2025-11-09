"""
Provider Manager for multi-provider LLM orchestration.

Handles:
- Provider initialization and health tracking
- Fallback mechanisms
- Intelligent routing (cost, capability, speed)
- Load balancing
"""

import logging
from typing import Type, TypeVar, Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime, timedelta

from consultantos.llm.provider_interface import LLMProvider
from consultantos.llm.gemini_provider import GeminiProvider
from consultantos.llm.openai_provider import OpenAIProvider
from consultantos.llm.anthropic_provider import AnthropicProvider

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ProviderHealth:
    """Track provider health and failure rates."""

    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.total_requests = 0
        self.failed_requests = 0
        self.last_failure = None
        self.consecutive_failures = 0
        self.is_healthy = True

    def record_success(self):
        """Record successful request."""
        self.total_requests += 1
        self.consecutive_failures = 0
        self.is_healthy = True

    def record_failure(self):
        """Record failed request."""
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_failure = datetime.now()

        # Mark unhealthy after 3 consecutive failures
        if self.consecutive_failures >= 3:
            self.is_healthy = False

    def get_failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests

    def should_retry(self) -> bool:
        """Determine if provider should be retried."""
        if self.is_healthy:
            return True

        # Retry after cooldown period (5 minutes)
        if self.last_failure:
            cooldown = timedelta(minutes=5)
            if datetime.now() - self.last_failure > cooldown:
                self.is_healthy = True
                self.consecutive_failures = 0
                return True

        return False


class ProviderManager:
    """
    Manage multiple LLM providers with intelligent routing.

    Supports:
    - Fallback on provider failure
    - Cost-based routing
    - Capability-based routing
    - Load balancing
    """

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        primary_provider: str = "gemini",
        enable_fallback: bool = True,
        routing_strategy: str = "fallback"
    ):
        """
        Initialize provider manager.

        Args:
            gemini_api_key: Google AI API key
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            primary_provider: Primary provider to use
            enable_fallback: Enable automatic fallback
            routing_strategy: Routing strategy (fallback, cost, capability, load_balance)
        """
        self.providers: Dict[str, LLMProvider] = {}
        self.health: Dict[str, ProviderHealth] = {}

        # Initialize providers
        if gemini_api_key:
            self.providers["gemini"] = GeminiProvider(gemini_api_key)
            self.health["gemini"] = ProviderHealth("gemini")

        if openai_api_key:
            self.providers["openai"] = OpenAIProvider(openai_api_key)
            self.health["openai"] = ProviderHealth("openai")

        if anthropic_api_key:
            self.providers["anthropic"] = AnthropicProvider(anthropic_api_key)
            self.health["anthropic"] = ProviderHealth("anthropic")

        self.primary_provider = primary_provider
        self.enable_fallback = enable_fallback
        self.routing_strategy = routing_strategy

        # Fallback order (used when primary fails)
        self.fallback_order = self._determine_fallback_order()

        logger.info(
            f"ProviderManager initialized",
            extra={
                "providers": list(self.providers.keys()),
                "primary": self.primary_provider,
                "fallback_enabled": self.enable_fallback,
                "routing_strategy": self.routing_strategy
            }
        )

    def _determine_fallback_order(self) -> List[str]:
        """
        Determine fallback order based on available providers.

        Returns:
            List of provider names in fallback order
        """
        all_providers = list(self.providers.keys())

        # Remove primary from list
        if self.primary_provider in all_providers:
            all_providers.remove(self.primary_provider)

        # Sort by cost (cheapest first for fallback)
        all_providers.sort(
            key=lambda p: self.providers[p].get_cost_per_token()
        )

        return all_providers

    async def generate(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Generate using configured routing strategy.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response

        Raises:
            Exception: If all providers fail
        """
        if self.routing_strategy == "cost":
            return await self.route_by_cost(
                prompt, response_model, temperature, max_tokens, **kwargs
            )
        elif self.routing_strategy == "capability":
            task_type = kwargs.pop("task_type", "analytical")
            return await self.route_by_capability(
                task_type, prompt, response_model, temperature, max_tokens, **kwargs
            )
        elif self.routing_strategy == "load_balance":
            return await self.route_by_load_balance(
                prompt, response_model, temperature, max_tokens, **kwargs
            )
        else:  # fallback strategy (default)
            return await self.generate_with_fallback(
                prompt, response_model, temperature, max_tokens, **kwargs
            )

    async def generate_with_fallback(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Try primary provider, fallback on failure.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response

        Raises:
            Exception: If all providers fail
        """
        providers_to_try = [self.primary_provider]
        if self.enable_fallback:
            providers_to_try.extend(self.fallback_order)

        last_error = None

        for provider_name in providers_to_try:
            if provider_name not in self.providers:
                continue

            # Check provider health
            if not self.health[provider_name].should_retry():
                logger.warning(
                    f"Skipping unhealthy provider: {provider_name}",
                    extra={"provider": provider_name}
                )
                continue

            try:
                provider = self.providers[provider_name]
                logger.info(
                    f"Attempting generation with {provider_name}",
                    extra={"provider": provider_name, "attempt": providers_to_try.index(provider_name) + 1}
                )

                result = await provider.generate(
                    prompt, response_model, temperature, max_tokens, **kwargs
                )

                # Record success
                self.health[provider_name].record_success()

                logger.info(
                    f"Generation successful with {provider_name}",
                    extra={
                        "provider": provider_name,
                        "tokens_used": provider.get_total_tokens_used(),
                        "cost_estimate": provider.estimate_cost(provider.get_total_tokens_used())
                    }
                )

                return result

            except Exception as e:
                last_error = e
                self.health[provider_name].record_failure()

                logger.warning(
                    f"Provider {provider_name} failed: {e}. Trying fallback...",
                    extra={"provider": provider_name, "error": str(e)}
                )
                continue

        # All providers failed
        logger.error(
            f"All LLM providers failed",
            extra={
                "providers_tried": providers_to_try,
                "last_error": str(last_error)
            }
        )
        raise Exception(f"All LLM providers failed. Last error: {last_error}")

    async def route_by_cost(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Route to cheapest available provider.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        # Find cheapest healthy provider
        healthy_providers = [
            (name, provider)
            for name, provider in self.providers.items()
            if self.health[name].should_retry()
        ]

        if not healthy_providers:
            raise Exception("No healthy providers available")

        cheapest = min(
            healthy_providers,
            key=lambda x: x[1].get_cost_per_token()
        )

        provider_name, provider = cheapest

        logger.info(
            f"Routing to cheapest provider: {provider_name}",
            extra={
                "provider": provider_name,
                "cost_per_1k": provider.get_cost_per_token()
            }
        )

        try:
            result = await provider.generate(
                prompt, response_model, temperature, max_tokens, **kwargs
            )
            self.health[provider_name].record_success()
            return result
        except Exception as e:
            self.health[provider_name].record_failure()
            # Fallback to next cheapest
            logger.warning(f"Cheapest provider failed, using fallback")
            return await self.generate_with_fallback(
                prompt, response_model, temperature, max_tokens, **kwargs
            )

    async def route_by_capability(
        self,
        task_type: str,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Route based on provider strengths.

        Args:
            task_type: Type of task (creative, analytical, speed)
            prompt: Input prompt
            response_model: Pydantic model for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        # Provider strength mapping
        routing_map = {
            "creative": "anthropic",      # Claude for creative writing
            "synthesis": "anthropic",      # Claude for synthesis
            "analytical": "openai",        # GPT-4 for deep analysis
            "reasoning": "openai",         # GPT-4 for complex reasoning
            "speed": "gemini",             # Gemini for fast responses
            "cost_effective": "gemini",    # Gemini for high volume
            "general": "gemini"            # Gemini as default
        }

        provider_name = routing_map.get(task_type, self.primary_provider)

        # Fallback if preferred provider not available or unhealthy
        if (provider_name not in self.providers or
            not self.health[provider_name].should_retry()):
            logger.warning(
                f"Preferred provider {provider_name} not available, using fallback"
            )
            return await self.generate_with_fallback(
                prompt, response_model, temperature, max_tokens, **kwargs
            )

        logger.info(
            f"Routing to capability-matched provider: {provider_name}",
            extra={"provider": provider_name, "task_type": task_type}
        )

        try:
            result = await self.providers[provider_name].generate(
                prompt, response_model, temperature, max_tokens, **kwargs
            )
            self.health[provider_name].record_success()
            return result
        except Exception as e:
            self.health[provider_name].record_failure()
            logger.warning(f"Capability-matched provider failed, using fallback")
            return await self.generate_with_fallback(
                prompt, response_model, temperature, max_tokens, **kwargs
            )

    async def route_by_load_balance(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Distribute load across healthy providers.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Generated response
        """
        # Find provider with lowest request count
        healthy_providers = [
            (name, provider, self.health[name])
            for name, provider in self.providers.items()
            if self.health[name].should_retry()
        ]

        if not healthy_providers:
            raise Exception("No healthy providers available")

        # Choose provider with fewest requests
        least_used = min(
            healthy_providers,
            key=lambda x: x[1].get_request_count()
        )

        provider_name, provider, _ = least_used

        logger.info(
            f"Load balancing to: {provider_name}",
            extra={
                "provider": provider_name,
                "request_count": provider.get_request_count()
            }
        )

        try:
            result = await provider.generate(
                prompt, response_model, temperature, max_tokens, **kwargs
            )
            self.health[provider_name].record_success()
            return result
        except Exception as e:
            self.health[provider_name].record_failure()
            logger.warning(f"Load-balanced provider failed, using fallback")
            return await self.generate_with_fallback(
                prompt, response_model, temperature, max_tokens, **kwargs
            )

    def get_provider_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all providers.

        Returns:
            Dictionary with provider statistics
        """
        stats = {}
        for name, provider in self.providers.items():
            health = self.health[name]
            stats[name] = {
                "is_healthy": health.is_healthy,
                "total_requests": health.total_requests,
                "failed_requests": health.failed_requests,
                "failure_rate": health.get_failure_rate(),
                "consecutive_failures": health.consecutive_failures,
                "tokens_used": provider.get_total_tokens_used(),
                "estimated_cost": provider.estimate_cost(provider.get_total_tokens_used()),
                "capabilities": provider.get_capabilities()
            }
        return stats

    def reset_provider_health(self, provider_name: str):
        """
        Reset health status for a provider.

        Args:
            provider_name: Name of provider to reset
        """
        if provider_name in self.health:
            self.health[provider_name] = ProviderHealth(provider_name)
            logger.info(f"Reset health for provider: {provider_name}")
