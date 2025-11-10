"""
API endpoints for conversational AI system
"""
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from consultantos.agents.conversational_agent import ConversationalAgent
from consultantos.models.conversational import (
    ConversationalRequest,
    ConversationalResponse,
    ConversationHistory,
    Conversation,
    Message
)
from consultantos.database import get_db_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversational", tags=["conversational"])


@router.post("/chat", response_model=ConversationalResponse)
async def chat(request: ConversationalRequest):
    """
    Conversational AI chat with RAG and query routing

    Features:
    - RAG-based retrieval from historical reports
    - Intelligent routing to specialized agents
    - Conversation history management
    - Source citation and transparency

    Args:
        request: ConversationalRequest with query and options

    Returns:
        ConversationalResponse with AI response and sources

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info(f"Chat request: {request.query[:100]}...")

        # Initialize agent
        agent = ConversationalAgent(timeout=60)

        # Prepare input data
        input_data = {
            "query": request.query,
            "conversation_id": request.conversation_id,
            "context_depth": request.context_depth or 5,
            "use_rag": request.use_rag if request.use_rag is not None else True,
            "filter_company": request.filter_company,
            "filter_industry": request.filter_industry
        }

        # Execute agent
        result = await agent.execute(input_data)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Agent execution failed")
            )

        # Return response
        response_data = result.get("data")
        return ConversationalResponse(**response_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(
    conversation_id: str,
    limit: Optional[int] = Query(50, ge=1, le=100, description="Max messages to return")
):
    """
    Get conversation history

    Args:
        conversation_id: Conversation identifier
        limit: Maximum number of messages to return (1-100)

    Returns:
        ConversationHistory with messages

    Raises:
        HTTPException: If conversation not found or on errors
    """
    try:
        logger.info(f"Fetching conversation history: {conversation_id}")

        db = get_db_service()
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        # Get conversation document
        conv_ref = db.collection("conversations").document(conversation_id)
        conv_doc = conv_ref.get()

        if not conv_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )

        # Parse conversation data
        conv_data = conv_doc.to_dict()
        messages_data = conv_data.get("messages", [])

        # Apply limit
        if len(messages_data) > limit:
            messages_data = messages_data[-limit:]

        # Convert to Message objects
        messages = [Message(**msg) for msg in messages_data]

        # Build conversation object
        conversation = Conversation(
            conversation_id=conversation_id,
            user_id=conv_data.get("user_id"),
            messages=messages,
            created_at=conv_data.get("created_at"),
            updated_at=conv_data.get("updated_at"),
            metadata=conv_data.get("metadata")
        )

        return ConversationHistory(
            conversation=conversation,
            message_count=len(messages)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get history endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{conversation_id}")
async def delete_conversation_history(conversation_id: str):
    """
    Delete conversation history

    Args:
        conversation_id: Conversation identifier

    Returns:
        Success message

    Raises:
        HTTPException: If conversation not found or on errors
    """
    try:
        logger.info(f"Deleting conversation history: {conversation_id}")

        db = get_db_service()
        if not db:
            raise HTTPException(
                status_code=503,
                detail="Database service unavailable"
            )

        # Check if conversation exists
        conv_ref = db.collection("conversations").document(conversation_id)
        conv_doc = conv_ref.get()

        if not conv_doc.exists:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {conversation_id} not found"
            )

        # Delete conversation
        conv_ref.delete()

        logger.info(f"Deleted conversation: {conversation_id}")
        return {
            "success": True,
            "message": f"Conversation {conversation_id} deleted",
            "conversation_id": conversation_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete history endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/index-report")
async def index_report_for_rag(
    report_id: str,
    content: str,
    company: Optional[str] = None,
    industry: Optional[str] = None,
    report_type: Optional[str] = None
):
    """
    Index a report for RAG retrieval

    This endpoint allows indexing reports into the vector store
    for future conversational queries.

    Args:
        report_id: Unique report identifier
        content: Report text content to index
        company: Company name
        industry: Industry
        report_type: Type of report

    Returns:
        Success message with document ID

    Raises:
        HTTPException: On indexing errors
    """
    try:
        logger.info(f"Indexing report for RAG: {report_id}")

        # Initialize agent to access retriever
        agent = ConversationalAgent()

        # Prepare metadata
        metadata = {
            "source": report_id,
            "company": company or "",
            "industry": industry or "",
            "report_type": report_type or ""
        }

        # Index document
        doc_id = await agent.retriever.index_document(
            content=content,
            metadata=metadata,
            doc_id=report_id
        )

        logger.info(f"Indexed report {report_id} as document {doc_id}")

        return {
            "success": True,
            "message": f"Report indexed successfully",
            "report_id": report_id,
            "doc_id": doc_id,
            "indexed_content_length": len(content)
        }

    except Exception as e:
        logger.error(f"Index report endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rag-stats")
async def get_rag_stats():
    """
    Get RAG system statistics

    Returns:
        Statistics about indexed documents

    Raises:
        HTTPException: On errors
    """
    try:
        agent = ConversationalAgent()

        # Get document count
        doc_count = await agent.retriever.count_documents()

        return {
            "total_documents": doc_count,
            "collection_name": agent.retriever.vector_store.collection_name,
            "embedding_model": agent.retriever.embedding_generator.model_name,
            "embedding_dimension": agent.retriever.embedding_generator.get_embedding_dimension()
        }

    except Exception as e:
        logger.error(f"RAG stats endpoint failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
