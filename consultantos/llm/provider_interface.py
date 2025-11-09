"""
Abstract base class for LLM providers.

Defines the contract all LLM providers must implement for structured output generation,
cost tracking, and rate limit information.
"""

from abc import ABC, abstractmethod
from typing import Type, TypeVar, Generic, Dict, Any, Optional
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class LLMProvider(ABC, Generic[T]):
    """
    Abstract base class for LLM providers.

    All concrete provider implementations (Gemini, OpenAI, Anthropic) must inherit
    from this class and implement the required methods.
    """

    def __init__(self, api_key: str, model: Optional[str] = None):
        """
        Initialize provider with API key and optional model override.

        Args:
            api_key: API key for the provider
            model: Optional model name override (uses default if not provided)
        """
        self.api_key = api_key
        self.model = model or self.get_default_model()
        self._total_tokens_used = 0
        self._request_count = 0

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Generate structured output from the LLM.

        Args:
            prompt: The prompt to send to the LLM
            response_model: Pydantic model class for structured output
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Instance of response_model with generated data

        Raises:
            Exception: If generation fails
        """
        pass

    @abstractmethod
    def get_cost_per_token(self) -> float:
        """
        Return cost per 1K tokens for this provider.

        Returns:
            Cost in USD per 1000 tokens
        """
        pass

    @abstractmethod
    def get_rate_limits(self) -> Dict[str, int]:
        """
        Return rate limit information for this provider.

        Returns:
            Dictionary with rate limit info:
            {
                "requests_per_minute": int,
                "tokens_per_minute": int,
                "requests_per_day": int
            }
        """
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """
        Return the default model name for this provider.

        Returns:
            Default model identifier
        """
        pass

    def get_provider_name(self) -> str:
        """
        Return the provider name (e.g., 'gemini', 'openai', 'anthropic').

        Returns:
            Provider name in lowercase
        """
        return self.__class__.__name__.replace("Provider", "").lower()

    def get_total_tokens_used(self) -> int:
        """
        Return total tokens used by this provider instance.

        Returns:
            Total tokens consumed
        """
        return self._total_tokens_used

    def get_request_count(self) -> int:
        """
        Return total number of requests made by this provider.

        Returns:
            Request count
        """
        return self._request_count

    def _track_usage(self, tokens_used: int):
        """
        Track token usage for this provider.

        Args:
            tokens_used: Number of tokens consumed in the request
        """
        self._total_tokens_used += tokens_used
        self._request_count += 1

    def estimate_cost(self, tokens: int) -> float:
        """
        Estimate cost for a given number of tokens.

        Args:
            tokens: Number of tokens to estimate cost for

        Returns:
            Estimated cost in USD
        """
        return (tokens / 1000) * self.get_cost_per_token()

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities and characteristics.

        Returns:
            Dictionary describing provider strengths and features
        """
        return {
            "provider": self.get_provider_name(),
            "model": self.model,
            "cost_per_1k_tokens": self.get_cost_per_token(),
            "rate_limits": self.get_rate_limits(),
        }
