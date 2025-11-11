"""
Base agent class for ConsultantOS agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import asyncio
import logging
from pydantic import BaseModel
import instructor
import google.generativeai as genai
from consultantos.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(
        self,
        name: str,
        timeout: int = 60,
    ) -> None:
        """
        Initialize base agent

        Args:
            name: Agent name/identifier
            timeout: Per-agent timeout in seconds (default: 60s)
        """
        self.name = name
        self.timeout = timeout

        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)

        # Create instructor client with Gemini
        self.client = instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name=settings.gemini_model or "gemini-1.5-flash-002"
            ),
            mode=instructor.Mode.GEMINI_JSON
        )

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> BaseModel:
        """
        Generate structured output using Gemini.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for structured output
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Structured response as instance of response_model

        Raises:
            Exception: If generation fails
        """
        result = await asyncio.to_thread(
            self.client.create,
            messages=[{"role": "user", "content": prompt}],
            response_model=response_model,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        return result

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with timeout

        Args:
            input_data: Input data for the agent

        Returns:
            Agent execution result with at least these keys:
            - success: bool indicating if execution was successful
            - data: Any result data from the agent
            - error: Optional error message if success is False

        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
            Exception: Other execution errors
        """
        try:
            return await asyncio.wait_for(
                self._execute_internal(input_data),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            logger.error(
                f"{self.name}: Execution timed out after {self.timeout}s",
                extra={"agent": self.name, "timeout": self.timeout}
            )
            raise asyncio.TimeoutError(
                f"{self.name} agent timed out after {self.timeout} seconds"
            )

    @abstractmethod
    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal execution method (implemented by subclasses)

        Args:
            input_data: Input data specific to the agent implementation

        Returns:
            Dict containing execution results with structure specific to each agent
        """
        pass
