"""
Pydantic models for conversational AI system
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """Single message in conversation"""
    role: MessageRole = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional message metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What are Tesla's competitive advantages?",
                "timestamp": "2025-11-09T12:00:00",
                "metadata": {}
            }
        }


class ConversationalRequest(BaseModel):
    """Request for conversational AI chat"""
    query: str = Field(..., min_length=1, description="User query or message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context continuity")
    context_depth: Optional[int] = Field(5, ge=1, le=20, description="Number of previous messages for context")
    use_rag: Optional[bool] = Field(True, description="Whether to use RAG for context retrieval")
    filter_company: Optional[str] = Field(None, description="Filter RAG results by company")
    filter_industry: Optional[str] = Field(None, description="Filter RAG results by industry")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are Tesla's main competitive advantages in the EV market?",
                "conversation_id": "conv_20251109_abc123",
                "context_depth": 5,
                "use_rag": True,
                "filter_company": "Tesla"
            }
        }


class SourceDocument(BaseModel):
    """Source document cited in response"""
    content: str = Field(..., description="Document content excerpt")
    source: str = Field(..., description="Document source identifier")
    company: Optional[str] = Field(None, description="Company name")
    industry: Optional[str] = Field(None, description="Industry")
    report_type: Optional[str] = Field(None, description="Report type")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Tesla's competitive advantage stems from vertical integration...",
                "source": "report_tesla_2024_q3",
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "report_type": "quarterly_analysis",
                "relevance_score": 0.92
            }
        }


class ConversationalResponse(BaseModel):
    """Response from conversational AI"""
    response: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation ID")
    sources: List[SourceDocument] = Field(default=[], description="Source documents cited")
    routed_to_agent: Optional[str] = Field(None, description="Agent query was routed to (if any)")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Response metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "Tesla's key competitive advantages include vertical integration, battery technology leadership, and the Supercharger network...",
                "conversation_id": "conv_20251109_abc123",
                "sources": [
                    {
                        "content": "Tesla's vertical integration strategy...",
                        "source": "report_tesla_2024_q3",
                        "company": "Tesla",
                        "industry": "Electric Vehicles",
                        "report_type": "quarterly_analysis",
                        "relevance_score": 0.92
                    }
                ],
                "routed_to_agent": None,
                "timestamp": "2025-11-09T12:00:00",
                "metadata": {"rag_enabled": True, "docs_retrieved": 3}
            }
        }


class Conversation(BaseModel):
    """Full conversation with history"""
    conversation_id: str = Field(..., description="Unique conversation identifier")
    user_id: Optional[str] = Field(None, description="User ID (if authenticated)")
    messages: List[Message] = Field(default=[], description="Conversation messages")
    created_at: datetime = Field(default_factory=datetime.now, description="Conversation creation time")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update time")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Conversation metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conv_20251109_abc123",
                "user_id": "user_xyz",
                "messages": [
                    {
                        "role": "user",
                        "content": "What are Tesla's competitive advantages?",
                        "timestamp": "2025-11-09T12:00:00"
                    },
                    {
                        "role": "assistant",
                        "content": "Tesla's key competitive advantages include...",
                        "timestamp": "2025-11-09T12:00:05"
                    }
                ],
                "created_at": "2025-11-09T12:00:00",
                "updated_at": "2025-11-09T12:00:05",
                "metadata": {}
            }
        }


class ConversationHistory(BaseModel):
    """Conversation history response"""
    conversation: Conversation = Field(..., description="Full conversation details")
    message_count: int = Field(..., description="Total number of messages")

    class Config:
        json_schema_extra = {
            "example": {
                "conversation": {
                    "conversation_id": "conv_20251109_abc123",
                    "messages": [],
                    "created_at": "2025-11-09T12:00:00",
                    "updated_at": "2025-11-09T12:00:00"
                },
                "message_count": 2
            }
        }
