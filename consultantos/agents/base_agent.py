"""
Base agent class for ConsultantOS agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import asyncio
import logging
import google.generativeai as genai
import instructor
from consultantos.config import settings

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(
        self,
        name: str,
        model: str = "gemini-2.0-flash-exp",
        timeout: int = 60
    ):
        """
        Initialize base agent
        
        Args:
            name: Agent name/identifier
            model: LLM model to use
            timeout: Per-agent timeout in seconds (default: 60s)
        """
        self.name = name
        self.model = model
        self.timeout = timeout
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError(f"GEMINI_API_KEY not found for {name}")
        
        # Configure Gemini client
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(model=self.model)
        
        # Patch with Instructor for structured outputs
        try:
            self.structured_client = instructor.from_gemini(
                client=self.client,
                mode=instructor.Mode.GEMINI_JSON
            )
        except (NotImplementedError, AttributeError) as e:
            # Fallback if instructor doesn't support this mode
            logger.warning(f"GEMINI_JSON mode not available, falling back to JSON mode: {e}")
            self.structured_client = instructor.patch(
                self.client,
                mode=instructor.Mode.JSON  # Use different fallback mode
            )
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with timeout
        
        Args:
            input_data: Input data for the agent
        
        Returns:
            Agent execution result
        
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
        """Internal execution method (implemented by subclasses)"""
        pass

