"""
Base agent class for ConsultantOS agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Type
import asyncio
import logging
from pydantic import BaseModel
from consultantos.config import settings
from consultantos.llm.provider_manager import ProviderManager
from consultantos.llm.cost_tracker import cost_tracker

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""

    # Class-level provider manager (shared across all agents)
    _provider_manager: Optional[ProviderManager] = None

    def __init__(
        self,
        name: str,
        timeout: int = 60,
        task_type: str = "analytical"
    ) -> None:
        """
        Initialize base agent

        Args:
            name: Agent name/identifier
            timeout: Per-agent timeout in seconds (default: 60s)
            task_type: Task type hint for capability-based routing
                      (creative, analytical, speed, synthesis, reasoning)
        """
        self.name = name
        self.timeout = timeout
        self.task_type = task_type

        # Initialize provider manager if not already initialized
        if BaseAgent._provider_manager is None:
            BaseAgent._provider_manager = ProviderManager(
                gemini_api_key=settings.gemini_api_key,
                openai_api_key=settings.openai_api_key,
                anthropic_api_key=settings.anthropic_api_key,
                primary_provider=settings.primary_llm_provider,
                enable_fallback=settings.enable_llm_fallback,
                routing_strategy=settings.llm_routing_strategy
            )

            # Set cost budgets if configured
            if settings.llm_daily_budget:
                cost_tracker.set_daily_budget(settings.llm_daily_budget)
            if settings.llm_monthly_budget:
                cost_tracker.set_monthly_budget(settings.llm_monthly_budget)

        self.llm = BaseAgent._provider_manager
    
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        user_id: Optional[str] = None,
        analysis_id: Optional[str] = None
    ) -> BaseModel:
        """
        Generate structured output using configured provider strategy.

        Args:
            prompt: Input prompt
            response_model: Pydantic model for structured output
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            user_id: Optional user identifier for cost tracking
            analysis_id: Optional analysis identifier for cost tracking

        Returns:
            Structured response as instance of response_model

        Raises:
            Exception: If generation fails
        """
        # Use routing strategy from settings or task type hint
        kwargs = {}
        if settings.llm_routing_strategy == "capability":
            kwargs["task_type"] = self.task_type

        result = await self.llm.generate(
            prompt=prompt,
            response_model=response_model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        # Track costs
        provider_stats = self.llm.get_provider_stats()
        for provider_name, stats in provider_stats.items():
            if stats["total_requests"] > 0:
                # Track most recently used provider
                await cost_tracker.track_usage(
                    provider=provider_name,
                    model=self.llm.providers[provider_name].model,
                    tokens_used=stats["tokens_used"],
                    cost_per_1k_tokens=self.llm.providers[provider_name].get_cost_per_token(),
                    user_id=user_id,
                    analysis_id=analysis_id,
                    agent_name=self.name
                )
                break

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