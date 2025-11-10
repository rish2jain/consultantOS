"""
Base agent class for ConsultantOS agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import asyncio
import logging
import time
from pydantic import BaseModel
import instructor
import google.generativeai as genai
from consultantos.config import settings

try:
    from consultantos.observability import SentryIntegration
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

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

        # Create Gemini model
        gemini_model = genai.GenerativeModel(
            model_name=settings.gemini_model or "gemini-1.5-flash-002"
        )
        
        # Create instructor client with Gemini
        self.client = instructor.from_gemini(
            gemini_model,
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
        Execute agent task with timeout and performance tracking

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
        # Start Sentry transaction for performance monitoring
        transaction = None
        if SENTRY_AVAILABLE:
            try:
                transaction = SentryIntegration.start_transaction(
                    name=f"{self.name}.execute",
                    op="agent.execution"
                )
                transaction.__enter__()

                # Set agent context
                SentryIntegration.set_agent_context(
                    agent_name=self.name,
                    timeout=self.timeout,
                )

                # Add breadcrumb for agent start
                SentryIntegration.add_breadcrumb(
                    message=f"Starting {self.name} execution",
                    category="agent",
                    level="info",
                    data={
                        "company": input_data.get("company"),
                        "industry": input_data.get("industry"),
                    }
                )
            except Exception as e:
                logger.debug(f"Failed to start Sentry transaction: {e}")

        start_time = time.time()

        try:
            result = await asyncio.wait_for(
                self._execute_internal(input_data),
                timeout=self.timeout
            )

            # Record successful execution
            execution_time = time.time() - start_time
            if SENTRY_AVAILABLE and transaction:
                try:
                    transaction.set_measurement("execution_time", execution_time, "second")
                    SentryIntegration.add_breadcrumb(
                        message=f"{self.name} completed successfully",
                        category="agent",
                        level="info",
                        data={"execution_time": execution_time}
                    )
                except Exception:
                    pass

            return result

        except asyncio.TimeoutError as e:
            logger.error(
                f"{self.name}: Execution timed out after {self.timeout}s",
                extra={"agent": self.name, "timeout": self.timeout}
            )

            # Capture timeout in Sentry
            if SENTRY_AVAILABLE:
                try:
                    SentryIntegration.add_breadcrumb(
                        message=f"{self.name} timed out",
                        category="agent",
                        level="error",
                        data={"timeout": self.timeout}
                    )
                    SentryIntegration.capture_exception(
                        e,
                        tag_agent_name=self.name,
                        tag_error_type="timeout",
                    )
                except Exception:
                    pass

            raise asyncio.TimeoutError(
                f"{self.name} agent timed out after {self.timeout} seconds"
            )

        except Exception as e:
            # Capture agent execution error in Sentry
            if SENTRY_AVAILABLE:
                try:
                    SentryIntegration.add_breadcrumb(
                        message=f"{self.name} failed with error",
                        category="agent",
                        level="error",
                        data={"error": str(e)}
                    )
                    SentryIntegration.capture_exception(
                        e,
                        tag_agent_name=self.name,
                        tag_error_type=type(e).__name__,
                    )
                except Exception:
                    pass
            raise

        finally:
            # End Sentry transaction
            if SENTRY_AVAILABLE and transaction:
                try:
                    transaction.__exit__(None, None, None)
                except Exception:
                    pass

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
