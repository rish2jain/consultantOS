"""
Anthropic Claude LLM provider implementation.

Uses instructor with Anthropic API for structured outputs.
"""

import logging
from typing import Type, TypeVar, Dict
import instructor
from anthropic import AsyncAnthropic
from pydantic import BaseModel

from consultantos.llm.provider_interface import LLMProvider

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class AnthropicProvider(LLMProvider[T]):
    """
    Anthropic Claude LLM provider.

    Features:
    - Excellent for creative and nuanced analysis
    - Strong writing and synthesis capabilities
    - Good for long-context tasks
    """

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key
            model: Model name (defaults to claude-3-opus)
        """
        super().__init__(api_key, model)
        self.client = instructor.from_anthropic(
            AsyncAnthropic(api_key=self.api_key)
        )

    def get_default_model(self) -> str:
        """Return default Anthropic model."""
        return "claude-3-opus-20240229"

    async def generate(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Generate structured output using Claude.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for response
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters

        Returns:
            Structured response as instance of response_model

        Raises:
            Exception: If generation fails
        """
        try:
            result = await self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_model=response_model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            # Track usage (estimate tokens)
            estimated_tokens = len(prompt.split()) * 1.3 + 500
            self._track_usage(int(estimated_tokens))

            logger.info(
                f"Anthropic generation successful",
                extra={
                    "provider": "anthropic",
                    "model": self.model,
                    "estimated_tokens": estimated_tokens
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Anthropic generation failed: {e}",
                extra={"provider": "anthropic", "error": str(e)}
            )
            raise

    def get_cost_per_token(self) -> float:
        """
        Return Claude Opus pricing.

        Returns:
            Cost per 1K tokens in USD
        """
        # Claude 3 Opus pricing (as of 2024)
        # Input: $15 per 1M tokens = $0.015 per 1K tokens
        # Output: $75 per 1M tokens = $0.075 per 1K tokens
        # Using blended rate
        return 0.045

    def get_rate_limits(self) -> Dict[str, int]:
        """
        Return Anthropic rate limits.

        Returns:
            Rate limit information
        """
        return {
            "requests_per_minute": 50,
            "tokens_per_minute": 100000,
            "requests_per_day": 5000
        }

    def get_capabilities(self) -> Dict:
        """
        Return Anthropic-specific capabilities.

        Returns:
            Capability information
        """
        caps = super().get_capabilities()
        caps.update({
            "strengths": ["creative", "synthesis", "long_context"],
            "best_for": ["writing", "summarization", "nuanced_analysis"],
            "max_context": 200000,  # 200K tokens
            "supports_vision": True,
            "supports_function_calling": True
        })
        return caps
