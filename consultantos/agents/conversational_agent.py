"""
Production Conversational Agent with RAG
Full-featured conversational AI with retrieval-augmented generation,
query routing, and conversation history management
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
from consultantos.agents.base_agent import BaseAgent
from consultantos.rag.retriever import RAGRetriever, DocumentResult
from consultantos.routing.agent_router import AgentRouter
from consultantos.routing.query_classifier import AgentIntent
from consultantos.models.conversational import (
    ConversationalResponse,
    SourceDocument,
    Message,
    MessageRole,
    Conversation
)

logger = logging.getLogger(__name__)


class ConversationalAgent(BaseAgent):
    """
    Production conversational AI agent with RAG and query routing

    Features:
    - RAG-based context retrieval from historical reports
    - Intelligent query routing to specialized agents
    - Conversation history management in Firestore
    - Source citation and transparency
    """

    def __init__(
        self,
        timeout: int = 60,
        rag_persist_directory: Optional[str] = "./data/chromadb"
    ):
        """
        Initialize conversational agent

        Args:
            timeout: Agent timeout in seconds
            rag_persist_directory: ChromaDB persistence directory
        """
        super().__init__(name="ConversationalAgent", timeout=timeout)

        # Initialize RAG retriever
        self.retriever = RAGRetriever(
            embedding_model="all-MiniLM-L6-v2",
            collection_name="consultantos_reports",
            persist_directory=rag_persist_directory
        )

        # Initialize query router
        self.router = AgentRouter()

        # Database service (lazy loaded)
        self._db_service = None

    def _get_db_service(self):
        """Lazy load database service"""
        if self._db_service is None:
            try:
                from consultantos.database import get_db_service
                self._db_service = get_db_service()
            except Exception as e:
                logger.warning(f"Failed to initialize database service: {e}")
                self._db_service = None
        return self._db_service

    async def _execute_internal(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute conversational query with RAG and routing

        Args:
            input_data: Dict with keys:
                - query: str (required)
                - conversation_id: str (optional)
                - context_depth: int (default: 5)
                - use_rag: bool (default: True)
                - filter_company: str (optional)
                - filter_industry: str (optional)

        Returns:
            Dict with success, data (ConversationalResponse), error
        """
        query = input_data.get("query", "")
        conversation_id = input_data.get("conversation_id") or self._generate_conversation_id()
        context_depth = input_data.get("context_depth", 5)
        use_rag = input_data.get("use_rag", True)
        filter_company = input_data.get("filter_company")
        filter_industry = input_data.get("filter_industry")

        if not query or not query.strip():
            return {
                "success": False,
                "error": "Query is required",
                "data": None
            }

        try:
            logger.info(f"Processing conversational query: {query[:100]}... (conv: {conversation_id})")

            # Step 1: Check if query should be routed to specialized agent
            route_intent = await self.router.classify_query(query)

            if route_intent and route_intent != AgentIntent.GENERAL:
                # Route to specialized agent
                logger.info(f"Routing to {route_intent.value} agent")
                return await self._handle_routed_query(
                    query=query,
                    conversation_id=conversation_id,
                    route_intent=route_intent,
                    input_data=input_data
                )

            # Step 2: Use RAG for general queries
            if use_rag:
                return await self._handle_rag_query(
                    query=query,
                    conversation_id=conversation_id,
                    context_depth=context_depth,
                    filter_company=filter_company,
                    filter_industry=filter_industry
                )
            else:
                # Direct LLM response without RAG
                return await self._handle_direct_query(
                    query=query,
                    conversation_id=conversation_id,
                    context_depth=context_depth
                )

        except Exception as e:
            logger.error(f"Conversational agent failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    async def _handle_routed_query(
        self,
        query: str,
        conversation_id: str,
        route_intent: AgentIntent,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle query routed to specialized agent"""

        # Execute routing
        agent_result = await self.router.execute_route(
            intent=route_intent,
            query=query,
            input_data=input_data
        )

        # Extract response text
        if agent_result.get("success"):
            # Format agent response
            agent_data = agent_result.get("data", {})
            response_text = self._format_agent_response(route_intent, agent_data)
        else:
            response_text = f"Agent routing failed: {agent_result.get('error', 'Unknown error')}"

        # Store conversation
        await self._store_message(conversation_id, MessageRole.USER, query)
        await self._store_message(conversation_id, MessageRole.ASSISTANT, response_text)

        # Create response
        response = ConversationalResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=[],
            routed_to_agent=route_intent.value,
            timestamp=datetime.now(),
            metadata={"agent_success": agent_result.get("success")}
        )

        return {
            "success": True,
            "data": response.model_dump(),
            "error": None
        }

    async def _handle_rag_query(
        self,
        query: str,
        conversation_id: str,
        context_depth: int,
        filter_company: Optional[str],
        filter_industry: Optional[str]
    ) -> Dict[str, Any]:
        """Handle query using RAG"""

        # Build metadata filter
        filter_metadata = {}
        if filter_company:
            filter_metadata["company"] = filter_company
        if filter_industry:
            filter_metadata["industry"] = filter_industry

        # Retrieve relevant documents
        try:
            relevant_docs = await self.retriever.retrieve(
                query=query,
                top_k=3,
                filter_metadata=filter_metadata if filter_metadata else None
            )
        except Exception as e:
            logger.warning(f"RAG retrieval failed, falling back to direct query: {e}")
            relevant_docs = []

        # Get conversation history for context
        history_messages = await self._get_conversation_history(
            conversation_id,
            limit=context_depth
        )

        # Build prompt with RAG context
        prompt = self._build_rag_prompt(query, relevant_docs, history_messages)

        # Generate response
        response_text = await self._generate_response(prompt)

        # Convert docs to SourceDocument models
        sources = [
            SourceDocument(
                content=doc.content[:500],  # Truncate for response
                source=doc.source,
                company=doc.company or "",
                industry=doc.industry or "",
                report_type=doc.report_type or "",
                relevance_score=1.0 - doc.distance  # Convert distance to relevance
            )
            for doc in relevant_docs
        ]

        # Store conversation
        await self._store_message(conversation_id, MessageRole.USER, query)
        await self._store_message(conversation_id, MessageRole.ASSISTANT, response_text)

        # Create response
        response = ConversationalResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=sources,
            routed_to_agent=None,
            timestamp=datetime.now(),
            metadata={
                "rag_enabled": True,
                "docs_retrieved": len(relevant_docs),
                "filter_company": filter_company,
                "filter_industry": filter_industry
            }
        )

        return {
            "success": True,
            "data": response.model_dump(),
            "error": None
        }

    async def _handle_direct_query(
        self,
        query: str,
        conversation_id: str,
        context_depth: int
    ) -> Dict[str, Any]:
        """Handle direct query without RAG"""

        # Get conversation history
        history_messages = await self._get_conversation_history(
            conversation_id,
            limit=context_depth
        )

        # Build prompt with history only
        prompt = self._build_direct_prompt(query, history_messages)

        # Generate response
        response_text = await self._generate_response(prompt)

        # Store conversation
        await self._store_message(conversation_id, MessageRole.USER, query)
        await self._store_message(conversation_id, MessageRole.ASSISTANT, response_text)

        # Create response
        response = ConversationalResponse(
            response=response_text,
            conversation_id=conversation_id,
            sources=[],
            routed_to_agent=None,
            timestamp=datetime.now(),
            metadata={"rag_enabled": False}
        )

        return {
            "success": True,
            "data": response.model_dump(),
            "error": None
        }

    def _build_rag_prompt(
        self,
        query: str,
        relevant_docs: List[DocumentResult],
        history_messages: List[Message]
    ) -> str:
        """Build prompt with RAG context"""

        # Build context from retrieved documents
        context = ""
        if relevant_docs:
            context = "### Relevant Context from Historical Reports:\n\n"
            for i, doc in enumerate(relevant_docs, 1):
                source_info = f"{doc.company} - {doc.report_type}" if doc.company else doc.source
                context += f"**Source {i}** ({source_info}):\n{doc.content}\n\n"

        # Build conversation history
        history = ""
        if history_messages:
            history = "### Recent Conversation:\n\n"
            for msg in history_messages[-5:]:  # Last 5 messages
                role_label = "You" if msg.role == MessageRole.USER else "Assistant"
                history += f"**{role_label}**: {msg.content}\n\n"

        # Build full prompt
        prompt = f"""You are a business intelligence assistant for ConsultantOS, specializing in competitive intelligence and strategic analysis.

Be professional, concise, and actionable. Cite sources when using information from context.

{context}

{history}

### Current Question:
{query}

Provide a helpful, professional response based on the context above. If context is provided, cite the sources. Focus on actionable business insights."""

        return prompt

    def _build_direct_prompt(self, query: str, history_messages: List[Message]) -> str:
        """Build prompt without RAG (history only)"""

        # Build conversation history
        history = ""
        if history_messages:
            history = "### Recent Conversation:\n\n"
            for msg in history_messages[-5:]:
                role_label = "You" if msg.role == MessageRole.USER else "Assistant"
                history += f"**{role_label}**: {msg.content}\n\n"

        # Build prompt
        prompt = f"""You are a business intelligence assistant for ConsultantOS, specializing in competitive intelligence and strategic analysis.

Be professional, concise, and actionable.

{history}

### Current Question:
{query}

Provide a helpful, professional response focusing on business strategy and competitive intelligence."""

        return prompt

    async def _generate_response(self, prompt: str) -> str:
        """Generate response using Gemini"""
        import google.generativeai as genai

        model = genai.GenerativeModel(model_name="gemini-2.0-flash-exp")

        # Configure safety settings
        safety_settings = {
            genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
            genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
        }

        import asyncio

        def _generate():
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 2048,
                },
                safety_settings=safety_settings
            )
            return response.text if response.text else "Unable to generate response."

        return await asyncio.to_thread(_generate)

    def _format_agent_response(self, intent: AgentIntent, agent_data: Dict[str, Any]) -> str:
        """Format specialized agent response for conversational output"""
        # Simple formatting - can be enhanced based on agent type
        if isinstance(agent_data, dict):
            # Extract key information
            summary = agent_data.get("summary", str(agent_data))
            return f"[{intent.value.upper()} ANALYSIS]\n\n{summary}"
        return str(agent_data)

    async def _store_message(
        self,
        conversation_id: str,
        role: MessageRole,
        content: str
    ) -> bool:
        """Store message in Firestore conversation history"""
        db = self._get_db_service()
        if not db:
            logger.warning("Database not available, message not persisted")
            return False

        try:
            message = Message(
                role=role,
                content=content,
                timestamp=datetime.now()
            )

            # Get or create conversation document
            conv_ref = db.collection("conversations").document(conversation_id)
            conv_doc = conv_ref.get()

            if conv_doc.exists:
                # Append to existing conversation
                conv_ref.update({
                    "messages": db.ArrayUnion([message.model_dump()]),
                    "updated_at": datetime.now()
                })
            else:
                # Create new conversation
                conversation = Conversation(
                    conversation_id=conversation_id,
                    messages=[message],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                conv_ref.set(conversation.model_dump())

            logger.debug(f"Stored {role.value} message in conversation {conversation_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            return False

    async def _get_conversation_history(
        self,
        conversation_id: str,
        limit: int = 5
    ) -> List[Message]:
        """Get conversation history from Firestore"""
        db = self._get_db_service()
        if not db:
            return []

        try:
            conv_ref = db.collection("conversations").document(conversation_id)
            conv_doc = conv_ref.get()

            if not conv_doc.exists:
                return []

            conv_data = conv_doc.to_dict()
            messages_data = conv_data.get("messages", [])

            # Convert to Message objects
            messages = [Message(**msg) for msg in messages_data]

            # Return last N messages
            return messages[-limit:] if len(messages) > limit else messages

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def _generate_conversation_id(self) -> str:
        """Generate unique conversation ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"conv_{timestamp}_{unique_id}"
