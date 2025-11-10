"""
Conversational Agent MVP for Hackathon
Minimal chat interface using Gemini 1.5 Flash
"""
import logging
from typing import Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.mvp import ChatResponse
from datetime import datetime

logger = logging.getLogger(__name__)


class ConversationalAgentMVP(BaseAgent):
    """
    Minimal conversational agent for MVP demo
    Uses direct Gemini API calls without RAG
    """

    def __init__(self, timeout: int = 30):
        """Initialize conversational agent"""
        super().__init__(name="ConversationalAgentMVP", timeout=timeout)
        # Simple in-memory conversation history
        self.conversation_history: Dict[str, list] = {}

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conversational query

        Args:
            input_data: Dict with 'query' and optional 'conversation_id'

        Returns:
            Dict with ChatResponse data
        """
        query = input_data.get("query", "")
        conversation_id = input_data.get("conversation_id", f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}")

        if not query:
            return {
                "success": False,
                "error": "Query is required",
                "data": None
            }

        try:
            # Get conversation history
            history = self.conversation_history.get(conversation_id, [])

            # Build context from history
            context = ""
            if history:
                context = "Previous conversation:\n"
                for msg in history[-5:]:  # Last 5 messages for context
                    context += f"User: {msg['user']}\nAssistant: {msg['assistant']}\n\n"

            # Build prompt with business intelligence focus
            prompt = f"""You are a business intelligence assistant helping consultants with strategic analysis.
Be concise, professional, and focus on actionable insights.

{context}

Current question: {query}

Provide a helpful, professional response focusing on business strategy and competitive intelligence."""

            # Generate response using Gemini
            import google.generativeai as genai
            # Use the latest stable model (gemini-2.5-flash)
            model = genai.GenerativeModel(model_name="gemini-2.5-flash")

            response = await self._generate_async(model, prompt)

            # Store in conversation history
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []

            self.conversation_history[conversation_id].append({
                "user": query,
                "assistant": response,
                "timestamp": datetime.now().isoformat()
            })

            # Limit conversation history to last 10 exchanges to prevent memory bloat
            if len(self.conversation_history[conversation_id]) > 10:
                self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-10:]

            # Create response object
            chat_response = ChatResponse(
                response=response,
                conversation_id=conversation_id,
                timestamp=datetime.now()
            )

            return {
                "success": True,
                "data": chat_response.model_dump(),
                "error": None
            }

        except Exception as e:
            logger.error(f"Conversational agent failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def _generate_async(self, model, prompt: str) -> str:
        """
        Generate response asynchronously

        Args:
            model: Gemini model instance
            prompt: Input prompt

        Returns:
            Generated text response
        """
        import asyncio

        def _generate_sync():
            import google.generativeai as genai

            # Configure safety settings to be less restrictive
            safety_settings = {
                genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            }

            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1024,
                },
                safety_settings=safety_settings
            )

            # Handle blocked responses
            if not response.text:
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    return f"Response blocked (reason: {candidate.finish_reason}). Please rephrase your query."
                return "Unable to generate response. Please try a different query."

            return response.text

        # Run synchronous generation in thread pool
        return await asyncio.to_thread(_generate_sync)
