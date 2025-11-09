"""
OpenAI LLM provider implementation.

Uses instructor with OpenAI API for structured outputs.
"""

import logging
from typing import Type, TypeVar, Dict
import instructor
from openai import AsyncOpenAI
from pydantic import BaseModel

from consultantos.llm.provider_interface import LLMProvider

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class OpenAIProvider(LLMProvider[T]):
    """
    OpenAI LLM provider.

    Features:
    - Excellent for complex analytical tasks
    - Strong reasoning capabilities
    - Good for multi-step analysis
    """

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name (defaults to gpt-4-turbo)
        """
        super().__init__(api_key, model)
        self.client = instructor.from_openai(
            AsyncOpenAI(api_key=self.api_key)
        )

    def get_default_model(self) -> str:
        """Return default OpenAI model."""
        return "gpt-4-turbo-preview"

    async def generate(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Generate structured output using OpenAI.

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
            result = await self.client.chat.completions.create(
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
                f"OpenAI generation successful",
                extra={
                    "provider": "openai",
                    "model": self.model,
                    "estimated_tokens": estimated_tokens
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"OpenAI generation failed: {e}",
                extra={"provider": "openai", "error": str(e)}
            )
            raise

    def get_cost_per_token(self) -> float:
        """
        Return GPT-4 Turbo pricing.

        Returns:
            Cost per 1K tokens in USD
        """
        # GPT-4 Turbo pricing (as of 2024)
        # Input: $10 per 1M tokens = $0.01 per 1K tokens
        # Output: $30 per 1M tokens = $0.03 per 1K tokens
        # Using blended rate
        return 0.02

    def get_rate_limits(self) -> Dict[str, int]:
        """
        Return OpenAI rate limits.

        Returns:
            Rate limit information
        """
        return {
            "requests_per_minute": 500,
            "tokens_per_minute": 150000,
            "requests_per_day": 10000
        }

    def get_capabilities(self) -> Dict:
        """
        Return OpenAI-specific capabilities.

        Returns:
            Capability information
        """
        caps = super().get_capabilities()
        caps.update({
            "strengths": ["analytical", "reasoning", "complex_tasks"],
            "best_for": ["deep_analysis", "multi_step_reasoning", "accuracy"],
            "max_context": 128000,  # 128K tokens
            "supports_vision": True,
            "supports_function_calling": True
        })
        return caps
