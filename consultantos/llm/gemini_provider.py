"""
Google Gemini LLM provider implementation.

Uses instructor with Google Generative AI for structured outputs.
"""

import asyncio
import logging
from typing import Type, TypeVar, Dict
import instructor
import google.generativeai as genai
from pydantic import BaseModel

from consultantos.llm.provider_interface import LLMProvider

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class GeminiProvider(LLMProvider[T]):
    """
    Google Gemini LLM provider.

    Features:
    - Fast response times
    - Good for general analysis
    - Cost-effective for high-volume usage
    """

    def __init__(self, api_key: str, model: str = None):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google AI API key
            model: Model name (defaults to gemini-1.5-pro)
        """
        super().__init__(api_key, model)
        genai.configure(api_key=self.api_key)
        self.client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=self.model,
                generation_config={"temperature": 0.7}
            ),
            mode=instructor.Mode.GEMINI_JSON
        )

    def get_default_model(self) -> str:
        """Return default Gemini model."""
        return "gemini-1.5-pro"

    async def generate(
        self,
        prompt: str,
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> T:
        """
        Generate structured output using Gemini.

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
            # Run in executor to avoid blocking async loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self.client.create(
                    messages=[{"role": "user", "content": prompt}],
                    response_model=response_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    **kwargs
                )
            )

            # Track usage (estimate tokens from prompt + response)
            estimated_tokens = len(prompt.split()) * 1.3 + 500
            self._track_usage(int(estimated_tokens))

            logger.info(
                f"Gemini generation successful",
                extra={
                    "provider": "gemini",
                    "model": self.model,
                    "estimated_tokens": estimated_tokens
                }
            )

            return result

        except Exception as e:
            logger.error(
                f"Gemini generation failed: {e}",
                extra={"provider": "gemini", "error": str(e)}
            )
            raise

    def get_cost_per_token(self) -> float:
        """
        Return Gemini Pro pricing.

        Returns:
            Cost per 1K tokens in USD
        """
        # Gemini 1.5 Pro pricing (as of 2024)
        # Input: $0.35 per 1M tokens = $0.00035 per 1K tokens
        # Output: $1.05 per 1M tokens = $0.00105 per 1K tokens
        # Using blended rate
        return 0.0007

    def get_rate_limits(self) -> Dict[str, int]:
        """
        Return Gemini rate limits.

        Returns:
            Rate limit information
        """
        return {
            "requests_per_minute": 60,
            "tokens_per_minute": 32000,
            "requests_per_day": 1500
        }

    def get_capabilities(self) -> Dict:
        """
        Return Gemini-specific capabilities.

        Returns:
            Capability information
        """
        caps = super().get_capabilities()
        caps.update({
            "strengths": ["speed", "cost_effective", "general_purpose"],
            "best_for": ["high_volume", "quick_analysis", "cost_optimization"],
            "max_context": 1048576,  # 1M tokens
            "supports_vision": True,
            "supports_function_calling": True
        })
        return caps
