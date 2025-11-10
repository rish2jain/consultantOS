# Phase 1 Skills Architecture - ConsultantOS

**Version**: 1.0
**Date**: 2025-01-09
**Status**: Design Complete

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture Overview](#system-architecture-overview)
3. [Skill 1: Conversational AI Interface](#skill-1-conversational-ai-interface)
4. [Skill 2: Enhanced Predictive Analytics](#skill-2-enhanced-predictive-analytics)
5. [Skill 3: Dark Data Mining](#skill-3-dark-data-mining)
6. [API Design](#api-design)
7. [Database Schema](#database-schema)
8. [Caching Strategy](#caching-strategy)
9. [Performance Targets](#performance-targets)
10. [Security & Privacy](#security--privacy)
11. [Testing Strategy](#testing-strategy)
12. [Deployment & Migration](#deployment--migration)

---

## Executive Summary

This document defines the production-ready architecture for integrating three Phase 1 skills into ConsultantOS:

1. **Conversational AI Interface**: Replace static dashboards with chat-based intelligence, natural language queries, and RAG over historical reports
2. **Enhanced Predictive Analytics**: Add forecasting UI with scenario simulation on top of existing Prophet anomaly detection
3. **Dark Data Mining**: Extract insights from unstructured internal data (emails, Slack, documents) to unlock the 90% of wasted data

**Key Integration Points**:
- Extends existing agent architecture (5 agents → 8 agents)
- Leverages existing monitoring infrastructure (IntelligenceMonitor, AnomalyDetector, EntityTracker)
- Reuses existing components (NLPProcessor, TimeSeriesOptimizer, AnalysisOrchestrator)
- Maintains backward compatibility (all existing APIs unchanged)

**Performance SLAs**:
- Conversational AI: <5s response time (p95), 100 concurrent conversations
- Predictive Analytics: <10s forecast generation (p95), <15s scenario simulation
- Dark Data Mining: <30s per 100 documents (p95), 10,000 documents/hour

**Resource Requirements**:
- Additional Cloud Run instances: 3 (one per skill)
- Memory: +9GB total (2GB conversational + 4GB forecasting + 3GB dark data)
- Storage: +2GB for embeddings, models, processed documents
- LLM tokens: +50,000 tokens/day avg

---

## System Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js 14)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Chat UI    │  │ Forecast UI  │  │  Dark Data Dashboard      │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└────────────────┬────────────────┬────────────────┬──────────────────┘
                 │                │                │
                 ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       FastAPI Backend                                │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    API Layer (Thin)                           │  │
│  │  /chat/*   /forecasting/*   /dark-data/*   (existing routes) │  │
│  └────────┬─────────────────┬───────────────────┬────────────────┘  │
│           │                 │                   │                    │
│  ┌────────▼────────┐  ┌────▼────────┐  ┌───────▼───────────┐       │
│  │Conversational   │  │ Forecasting │  │  DarkData        │       │
│  │Agent            │  │ Agent       │  │  Agent           │       │
│  └────────┬────────┘  └────┬────────┘  └───────┬───────────┘       │
│           │                 │                   │                    │
│  ┌────────▼─────────────────▼───────────────────▼──────────────┐   │
│  │              AnalysisOrchestrator (Extended)                 │   │
│  │  Phase 1: Research + Market + Financial (parallel)           │   │
│  │  Phase 2: Framework (sequential)                             │   │
│  │  Phase 3: Synthesis (sequential)                             │   │
│  │  Phase 4: Conversational/Forecasting/DarkData (conditional)  │   │
│  └────────────────────────────┬──────────────────────────────────┘  │
└────────────────────────────────┼─────────────────────────────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
        ▼                        ▼                        ▼
┌───────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  RAG System   │    │ TimeSeriesOpt    │    │ DataConnectors   │
│  (Embeddings) │    │ AnomalyDetector  │    │ (Gmail/Slack)    │
└───────┬───────┘    └────────┬─────────┘    └────────┬─────────┘
        │                     │                       │
        ▼                     ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        Firestore Database                            │
│  conversations │ forecasts │ dark_data_sources │ (existing tables)  │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

**Conversational AI**:
```
User Query → ConversationalAgent.parse_query()
          → QueryRouter.classify_intent()
          → [Research/Market/Financial Agents] (parallel)
          → RAGSystem.augment_context()
          → Gemini.generate_response()
          → ConversationStateManager.save()
          → SSE Stream to Frontend
```

**Predictive Analytics**:
```
User Request → ForecastingAgent.execute()
            → TimeSeriesOptimizer.get_timeseries()
            → AnomalyDetector.forecast() (Prophet)
            → ScenarioSimulator.run_scenarios()
            → ForecastMetricsStore.save()
            → Visualization API
```

**Dark Data Mining**:
```
Schedule Trigger → DarkDataAgent.execute()
                 → DataConnectors.extract() (Gmail/Slack/Drive)
                 → DarkDataProcessor.analyze() (NLP)
                 → EntityTracker.update()
                 → DarkDataStore.save()
                 → IntelligenceMonitor.integrate_signals()
                 → Alert if threshold exceeded
```

### Integration with Existing System

| Existing Component | Integration Point | Changes Required |
|-------------------|-------------------|------------------|
| AnalysisOrchestrator | Add Phase 4 (optional conversational/forecasting/dark data) | Minimal: Add conditional phase execution |
| IntelligenceMonitor | Integrate dark data signals into change detection | Extend: Add `dark_data_signals` field |
| AnomalyDetector | Add forecast() method using existing Prophet models | Extend: Expose forecast generation API |
| EntityTracker | Feed dark data entities | Extend: Accept entities from DarkDataProcessor |
| NLPProcessor | Reuse for dark data processing | No change: Already supports entity extraction |
| TimeSeriesOptimizer | Expose get_timeseries() for ForecastingAgent | Minimal: Make method public |
| BaseAgent | New agents inherit from BaseAgent | No change: Standard inheritance pattern |
| Firestore DB | Add new collections | Extend: 8 new collections (see Database Schema) |
| Cache | Extend for conversations, forecasts, dark data | Extend: Add cache keys and invalidation rules |

---

## Skill 1: Conversational AI Interface

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Conversational AI System                        │
│                                                                      │
│  ┌────────────────┐         ┌────────────────┐                     │
│  │ Query Parser   │ ─────▶  │ Intent         │                     │
│  │ (Gemini)       │         │ Classifier     │                     │
│  └────────────────┘         └────────┬───────┘                     │
│                                      │                              │
│                                      ▼                              │
│  ┌────────────────┐         ┌────────────────┐                     │
│  │ RAG System     │ ◀────── │ Query Router   │                     │
│  │ (Vector Search)│         │ (Route to      │                     │
│  └────────┬───────┘         │  Agents)       │                     │
│           │                 └────────┬───────┘                     │
│           │                          │                              │
│           │                          ▼                              │
│           │         ┌────────────────────────────────┐             │
│           │         │  Existing Agents (Parallel)    │             │
│           │         │  Research | Market | Financial │             │
│           │         └────────────┬───────────────────┘             │
│           │                      │                                  │
│           │                      ▼                                  │
│           └─────────▶ ┌──────────────────────┐                    │
│                       │ Response Generator   │                    │
│                       │ (Gemini + RAG)       │                    │
│                       └──────────┬───────────┘                    │
│                                  │                                  │
│                                  ▼                                  │
│                       ┌──────────────────────┐                    │
│                       │ ConversationState    │                    │
│                       │ Manager (Firestore)  │                    │
│                       └──────────────────────┘                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.1 ConversationalAgent

**Purpose**: Orchestrate conversational intelligence flow

**Implementation**:
```python
# consultantos/agents/conversational_agent.py

from typing import Optional, List, Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.conversational import (
    ConversationQuery,
    ConversationResponse,
    QueryIntent,
    ConversationContext
)
from consultantos.utils.query_router import QueryRouter
from consultantos.utils.rag_system import RAGSystem
from consultantos.utils.conversation_state import ConversationStateManager
import instructor
from pydantic import BaseModel

class ConversationalAgent(BaseAgent):
    """Agent for handling conversational intelligence queries."""

    def __init__(self, orchestrator=None, rag_system=None, state_manager=None):
        super().__init__(agent_name="conversational")
        self.orchestrator = orchestrator
        self.rag_system = rag_system or RAGSystem()
        self.state_manager = state_manager or ConversationStateManager()
        self.query_router = QueryRouter()

    async def _execute_internal(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> ConversationResponse:
        """Execute conversational query with multi-turn context."""

        # Load conversation context if exists
        context = await self.state_manager.load_context(
            conversation_id=conversation_id,
            user_id=user_id
        )

        # Parse query and classify intent
        parsed_query = await self._parse_query(query, context)

        # Route query to appropriate agents
        agent_results = await self._route_query(parsed_query, context)

        # Augment with RAG context
        rag_context = await self.rag_system.retrieve_relevant_context(
            query=query,
            company=parsed_query.entities.get("company"),
            top_k=3
        )

        # Generate response with Gemini
        response = await self._generate_response(
            query=query,
            parsed_query=parsed_query,
            agent_results=agent_results,
            rag_context=rag_context,
            context=context
        )

        # Save conversation state
        await self.state_manager.save_message(
            conversation_id=conversation_id or response.conversation_id,
            user_id=user_id,
            role="user",
            content=query,
            metadata={"parsed_query": parsed_query.dict()}
        )

        await self.state_manager.save_message(
            conversation_id=response.conversation_id,
            user_id=user_id,
            role="assistant",
            content=response.response_text,
            metadata={
                "agents_used": response.agents_used,
                "response_time": response.response_time,
                "tokens_used": response.tokens_used
            }
        )

        return response

    async def _parse_query(
        self,
        query: str,
        context: ConversationContext
    ) -> ConversationQuery:
        """Parse query with intent classification and entity extraction."""

        # Build prompt with conversation context
        context_summary = context.get_summary() if context else ""

        prompt = f"""Analyze this user query and extract structured information.

Previous conversation context:
{context_summary}

User query: {query}

Extract:
1. Intent type: comparison, trend, forecast, explain, deep_dive, follow_up
2. Entities: companies, industries, metrics, timeframes
3. Depth level: simple, moderate, detailed
4. Follow-up context: If this is a follow-up, what does "it", "they", "their" refer to?
"""

        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            response_model=ConversationQuery,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        return response

    async def _route_query(
        self,
        parsed_query: ConversationQuery,
        context: ConversationContext
    ) -> Dict[str, Any]:
        """Route query to appropriate agents based on intent."""

        agents_to_call = self.query_router.route(parsed_query)

        if not self.orchestrator:
            return {}

        # Call agents in parallel through orchestrator
        results = {}
        if "research" in agents_to_call:
            results["research"] = await self.orchestrator.research_agent.execute(
                company=parsed_query.entities.get("company", ""),
                industry=parsed_query.entities.get("industry", "")
            )

        if "market" in agents_to_call:
            results["market"] = await self.orchestrator.market_agent.execute(
                company=parsed_query.entities.get("company", ""),
                industry=parsed_query.entities.get("industry", "")
            )

        if "financial" in agents_to_call:
            results["financial"] = await self.orchestrator.financial_agent.execute(
                company=parsed_query.entities.get("company", ""),
                industry=parsed_query.entities.get("industry", "")
            )

        return results

    async def _generate_response(
        self,
        query: str,
        parsed_query: ConversationQuery,
        agent_results: Dict[str, Any],
        rag_context: List[Dict[str, Any]],
        context: ConversationContext
    ) -> ConversationResponse:
        """Generate conversational response with Gemini."""

        # Build comprehensive prompt
        agent_context = "\n".join([
            f"{agent}: {result.summary if hasattr(result, 'summary') else str(result)[:200]}"
            for agent, result in agent_results.items()
        ])

        rag_context_text = "\n".join([
            f"- {doc['chunk_text'][:300]}... (from {doc['metadata']['company']} report)"
            for doc in rag_context
        ])

        conversation_history = context.get_recent_messages(n=5) if context else []

        depth_instruction = {
            "simple": "Explain like I'm 5 - use simple language, avoid jargon",
            "moderate": "Use professional language, balance detail with clarity",
            "detailed": "Provide comprehensive technical analysis with data support"
        }.get(parsed_query.depth_level, "Use professional language")

        prompt = f"""You are an AI competitive intelligence analyst. Answer the user's query conversationally.

User query: {query}

Conversation history:
{conversation_history}

Agent analysis results:
{agent_context}

Relevant historical reports:
{rag_context_text}

Instructions:
- {depth_instruction}
- Be conversational and engaging
- Cite sources when using historical data
- Suggest relevant follow-up questions
- If data is missing, acknowledge limitations

Respond naturally in a conversational tone.
"""

        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.7
        )

        response_text = response.choices[0].message.content

        # Generate follow-up suggestions
        followups = await self._generate_followups(query, parsed_query, agent_results)

        return ConversationResponse(
            conversation_id=context.conversation_id if context else None,
            response_text=response_text,
            agents_used=list(agent_results.keys()),
            rag_documents_used=len(rag_context),
            suggested_followups=followups,
            response_time=0.0,  # Will be set by caller
            tokens_used=response.usage.total_tokens
        )

    async def _generate_followups(
        self,
        query: str,
        parsed_query: ConversationQuery,
        agent_results: Dict[str, Any]
    ) -> List[str]:
        """Generate relevant follow-up questions."""

        prompt = f"""Based on this query and analysis, suggest 3 relevant follow-up questions.

Query: {query}
Intent: {parsed_query.intent}
Entities: {parsed_query.entities}

Suggest questions that:
1. Dig deeper into the analysis
2. Explore related aspects
3. Compare with competitors

Return only the questions, one per line.
"""

        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )

        followups = [
            q.strip()
            for q in response.choices[0].message.content.split("\n")
            if q.strip()
        ][:3]

        return followups
```

### 1.2 RAG System

**Purpose**: Semantic search over historical reports for context augmentation

**Implementation**:
```python
# consultantos/utils/rag_system.py

from typing import List, Dict, Any, Optional
import numpy as np
from google import genai
from consultantos.database import get_database
from consultantos.cache import cache
import hashlib

class RAGSystem:
    """Retrieval Augmented Generation system for historical reports."""

    def __init__(self):
        self.db = get_database()
        self.embedding_model = "models/text-embedding-004"
        self.chunk_size = 1000  # characters
        self.overlap = 200  # character overlap between chunks

    async def index_report(
        self,
        report_id: str,
        report_content: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Index a report for RAG retrieval."""

        # Chunk the report
        chunks = self._chunk_text(report_content)

        # Generate embeddings for each chunk
        documents_indexed = 0
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = await self._generate_embedding(chunk)

            # Store in Firestore
            doc_data = {
                "report_id": report_id,
                "chunk_index": i,
                "chunk_text": chunk,
                "embedding_vector": embedding.tolist(),
                "metadata": metadata,
                "indexed_at": firestore.SERVER_TIMESTAMP
            }

            await self.db.collection("rag_documents").add(doc_data)
            documents_indexed += 1

        return documents_indexed

    async def retrieve_relevant_context(
        self,
        query: str,
        company: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve most relevant document chunks for query."""

        # Generate query embedding
        query_embedding = await self._generate_embedding(query)

        # Search in Firestore
        # Note: Firestore vector search requires additional setup
        # For MVP, use semantic cache or external vector DB (Pinecone/Weaviate)

        # Filter by company if specified
        query_ref = self.db.collection("rag_documents")
        if company:
            query_ref = query_ref.where("metadata.company", "==", company)

        # Get all documents (for MVP - replace with vector search)
        docs = await query_ref.get()

        # Calculate cosine similarity
        results = []
        for doc in docs:
            data = doc.to_dict()
            doc_embedding = np.array(data["embedding_vector"])

            similarity = self._cosine_similarity(query_embedding, doc_embedding)

            results.append({
                "chunk_text": data["chunk_text"],
                "metadata": data["metadata"],
                "similarity": similarity
            })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            # Try to end at sentence boundary
            if end < len(text):
                last_period = chunk.rfind(". ")
                if last_period > self.chunk_size * 0.7:  # At least 70% of chunk
                    chunk = chunk[:last_period + 1]
                    end = start + last_period + 1

            chunks.append(chunk.strip())
            start = end - self.overlap  # Overlap for context

        return chunks

    @cache.memoize(ttl=86400)  # Cache embeddings for 24 hours
    async def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding vector for text."""

        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

        response = client.models.generate_embedding(
            model=self.embedding_model,
            content=text
        )

        return np.array(response.embedding)

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
```

### 1.3 Data Models

```python
# consultantos/models/conversational.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class QueryIntent(str, Enum):
    """Types of user query intents."""
    COMPARISON = "comparison"  # Compare companies/products
    TREND = "trend"  # Market trends, sentiment trends
    FORECAST = "forecast"  # Predictive questions
    EXPLAIN = "explain"  # Explain analysis/data
    DEEP_DIVE = "deep_dive"  # Detailed investigation
    FOLLOW_UP = "follow_up"  # Follow-up to previous query

class ConversationQuery(BaseModel):
    """Parsed user query with structured information."""
    intent: QueryIntent
    entities: Dict[str, str] = Field(
        description="Extracted entities: company, industry, metric, timeframe"
    )
    depth_level: str = Field(
        default="moderate",
        description="simple | moderate | detailed"
    )
    requires_agents: List[str] = Field(
        default=[],
        description="Which agents are needed: research, market, financial, framework"
    )
    follow_up_context: Optional[Dict[str, str]] = Field(
        default=None,
        description="Resolved references from previous conversation"
    )

class ConversationResponse(BaseModel):
    """Conversational AI response."""
    conversation_id: Optional[str] = None
    response_text: str
    agents_used: List[str] = []
    rag_documents_used: int = 0
    suggested_followups: List[str] = []
    response_time: float
    tokens_used: int
    confidence_score: Optional[float] = None

class ConversationContext(BaseModel):
    """Multi-turn conversation context."""
    conversation_id: str
    user_id: str
    messages: List[Dict[str, Any]] = []
    entities_mentioned: Dict[str, List[str]] = {}  # Track all entities mentioned
    last_intent: Optional[QueryIntent] = None
    created_at: datetime
    updated_at: datetime

    def get_summary(self, max_messages: int = 5) -> str:
        """Get concise summary of recent conversation."""
        recent = self.messages[-max_messages:] if len(self.messages) > max_messages else self.messages

        summary_lines = []
        for msg in recent:
            role = msg["role"]
            content = msg["content"][:100]  # Truncate
            summary_lines.append(f"{role}: {content}...")

        return "\n".join(summary_lines)

    def get_recent_messages(self, n: int = 5) -> str:
        """Get recent messages for context."""
        recent = self.messages[-n:] if len(self.messages) > n else self.messages
        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent
        ])

class ConversationCreate(BaseModel):
    """Request to create new conversation."""
    user_id: str
    initial_query: Optional[str] = None

class ConversationMessage(BaseModel):
    """Message in a conversation."""
    conversation_id: str
    query: str
    stream: bool = Field(default=False, description="Enable SSE streaming")
```

### 1.4 API Endpoints

```python
# consultantos/api/chat_endpoints.py

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from consultantos.models.conversational import (
    ConversationCreate,
    ConversationMessage,
    ConversationResponse
)
from consultantos.agents.conversational_agent import ConversationalAgent
from consultantos.auth import get_current_user
from consultantos.utils.conversation_state import ConversationStateManager
import asyncio
import json
import time

router = APIRouter(prefix="/chat", tags=["conversational-ai"])

@router.post("/conversations", response_model=Dict[str, str])
async def create_conversation(
    request: ConversationCreate,
    user=Depends(get_current_user)
):
    """Create a new conversation."""

    state_manager = ConversationStateManager()

    conversation_id = await state_manager.create_conversation(
        user_id=request.user_id,
        initial_query=request.initial_query
    )

    return {
        "conversation_id": conversation_id,
        "created_at": datetime.utcnow().isoformat()
    }

@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    message: ConversationMessage,
    user=Depends(get_current_user)
):
    """Send a message in conversation (streaming or non-streaming)."""

    if message.stream:
        # Return SSE stream
        return EventSourceResponse(
            _stream_response(conversation_id, message.query, user.user_id)
        )
    else:
        # Return complete response
        agent = ConversationalAgent()

        start_time = time.time()
        response = await agent.execute(
            query=message.query,
            conversation_id=conversation_id,
            user_id=user.user_id
        )
        response.response_time = time.time() - start_time

        return response

async def _stream_response(
    conversation_id: str,
    query: str,
    user_id: str
):
    """Stream conversational response using SSE."""

    agent = ConversationalAgent()

    # This is simplified - actual implementation would stream from Gemini
    response = await agent.execute(
        query=query,
        conversation_id=conversation_id,
        user_id=user_id
    )

    # Simulate streaming (chunk the response)
    words = response.response_text.split()
    for i in range(0, len(words), 5):  # Stream 5 words at a time
        chunk = " ".join(words[i:i+5])
        yield {
            "event": "message",
            "data": json.dumps({"chunk": chunk})
        }
        await asyncio.sleep(0.1)  # Simulate typing delay

    # Send final metadata
    yield {
        "event": "done",
        "data": json.dumps({
            "agents_used": response.agents_used,
            "suggested_followups": response.suggested_followups,
            "tokens_used": response.tokens_used
        })
    }

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    user=Depends(get_current_user)
):
    """Get conversation history."""

    state_manager = ConversationStateManager()

    conversation = await state_manager.load_conversation(
        conversation_id=conversation_id,
        user_id=user.user_id
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation

@router.get("/conversations")
async def list_conversations(
    user=Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """List user's conversations."""

    state_manager = ConversationStateManager()

    conversations = await state_manager.list_conversations(
        user_id=user.user_id,
        limit=limit,
        offset=offset
    )

    return {
        "conversations": conversations,
        "total": len(conversations),
        "limit": limit,
        "offset": offset
    }

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user=Depends(get_current_user)
):
    """Delete a conversation."""

    state_manager = ConversationStateManager()

    await state_manager.delete_conversation(
        conversation_id=conversation_id,
        user_id=user.user_id
    )

    return {"status": "deleted"}

@router.post("/rag/index")
async def index_report_for_rag(
    report_id: str,
    user=Depends(get_current_user)
):
    """Index a report for RAG retrieval (async job)."""

    # Enqueue indexing job
    from consultantos.jobs.queue import enqueue_job

    job_id = await enqueue_job(
        job_type="rag_indexing",
        payload={"report_id": report_id, "user_id": user.user_id}
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Report indexing started"
    }

@router.get("/suggestions")
async def get_suggestions(
    query: str,
    user=Depends(get_current_user)
):
    """Get suggested follow-up questions for a query."""

    agent = ConversationalAgent()

    # Generate suggestions without full execution
    suggestions = await agent._generate_followups(
        query=query,
        parsed_query=ConversationQuery(intent=QueryIntent.EXPLAIN, entities={}),
        agent_results={}
    )

    return {"suggestions": suggestions}
```

---

## Skill 2: Enhanced Predictive Analytics

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Predictive Analytics System                        │
│                                                                      │
│  ┌────────────────┐         ┌────────────────┐                     │
│  │ Forecasting    │ ─────▶  │ TimeSeriesOpt  │                     │
│  │ Agent          │         │ (Historical)   │                     │
│  └────────┬───────┘         └────────┬───────┘                     │
│           │                          │                              │
│           │                          ▼                              │
│           │         ┌────────────────────────────────┐             │
│           │         │  AnomalyDetector (Prophet)     │             │
│           │         │  - Train models                │             │
│           │         │  - Generate forecasts          │             │
│           │         │  - Confidence intervals        │             │
│           │         └────────────┬───────────────────┘             │
│           │                      │                                  │
│           ▼                      ▼                                  │
│  ┌────────────────────────────────────────────┐                    │
│  │          Scenario Simulator                │                    │
│  │  - Price change scenarios                  │                    │
│  │  - Market expansion scenarios              │                    │
│  │  - Competitor action scenarios             │                    │
│  │  - Monte Carlo simulation                  │                    │
│  └────────────────┬───────────────────────────┘                    │
│                   │                                                  │
│                   ▼                                                  │
│  ┌────────────────────────────────┐                                │
│  │  ForecastMetricsStore          │                                │
│  │  (Firestore)                   │                                │
│  └────────────────────────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.1 ForecastingAgent

**Purpose**: Generate forecasts using existing Prophet models

**Implementation**:
```python
# consultantos/agents/forecasting_agent.py

from typing import Optional, List, Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.forecasting import (
    ForecastRequest,
    ForecastResponse,
    ForecastMetric,
    ScenarioParameters
)
from consultantos.monitoring.anomaly_detector import AnomalyDetector
from consultantos.monitoring.timeseries_optimizer import TimeSeriesOptimizer
from consultantos.utils.scenario_simulator import ScenarioSimulator
import pandas as pd
from datetime import datetime, timedelta

class ForecastingAgent(BaseAgent):
    """Agent for generating predictive forecasts."""

    def __init__(self):
        super().__init__(agent_name="forecasting")
        self.anomaly_detector = AnomalyDetector()
        self.timeseries_optimizer = TimeSeriesOptimizer()
        self.scenario_simulator = ScenarioSimulator()

    async def _execute_internal(
        self,
        company: str,
        monitor_id: Optional[str] = None,
        metrics: List[ForecastMetric] = None,
        horizon_months: int = 6,
        scenarios: Optional[List[ScenarioParameters]] = None,
        **kwargs
    ) -> ForecastResponse:
        """Generate forecasts for specified metrics and scenarios."""

        # Default metrics if not specified
        if not metrics:
            metrics = [
                ForecastMetric.REVENUE,
                ForecastMetric.MARKET_SHARE,
                ForecastMetric.SENTIMENT
            ]

        # Get historical data
        historical_data = await self._get_historical_data(
            company=company,
            monitor_id=monitor_id,
            metrics=metrics
        )

        # Generate base forecasts
        forecasts = {}
        for metric in metrics:
            if metric.value not in historical_data:
                continue

            forecast = await self._generate_forecast(
                metric=metric,
                data=historical_data[metric.value],
                horizon_months=horizon_months
            )

            forecasts[metric.value] = forecast

        # Run scenario simulations if requested
        scenario_results = {}
        if scenarios:
            for scenario in scenarios:
                scenario_results[scenario.name] = await self.scenario_simulator.simulate(
                    base_forecasts=forecasts,
                    parameters=scenario,
                    horizon_months=horizon_months
                )

        # Calculate forecast accuracy if we have actual data
        accuracy_metrics = await self._calculate_accuracy(
            company=company,
            monitor_id=monitor_id,
            forecasts=forecasts
        )

        return ForecastResponse(
            company=company,
            monitor_id=monitor_id,
            forecasts=forecasts,
            scenarios=scenario_results,
            accuracy_metrics=accuracy_metrics,
            horizon_months=horizon_months,
            generated_at=datetime.utcnow()
        )

    async def _get_historical_data(
        self,
        company: str,
        monitor_id: Optional[str],
        metrics: List[ForecastMetric]
    ) -> Dict[str, pd.DataFrame]:
        """Get historical time series data for forecasting."""

        historical_data = {}

        for metric in metrics:
            # Use TimeSeriesOptimizer to get optimized historical data
            data = await self.timeseries_optimizer.get_timeseries(
                monitor_id=monitor_id,
                metric_name=metric.value,
                lookback_days=365  # 1 year of history
            )

            if data is not None and not data.empty:
                historical_data[metric.value] = data

        return historical_data

    async def _generate_forecast(
        self,
        metric: ForecastMetric,
        data: pd.DataFrame,
        horizon_months: int
    ) -> Dict[str, Any]:
        """Generate forecast for a single metric using Prophet."""

        # Prepare data for Prophet (requires 'ds' and 'y' columns)
        prophet_data = pd.DataFrame({
            'ds': data.index,
            'y': data.values
        })

        # Use AnomalyDetector's Prophet model
        # Note: AnomalyDetector needs to expose forecast() method
        forecast_df = await self.anomaly_detector.forecast(
            data=prophet_data,
            periods=horizon_months * 30,  # Approximate days
            freq='D'
        )

        # Extract forecast values with confidence intervals
        forecast_values = []
        for _, row in forecast_df.iterrows():
            forecast_values.append({
                "date": row['ds'].isoformat(),
                "predicted_value": float(row['yhat']),
                "lower_bound": float(row['yhat_lower']),
                "upper_bound": float(row['yhat_upper']),
                "confidence_interval": 0.95  # Prophet default
            })

        return {
            "metric": metric.value,
            "forecast_values": forecast_values,
            "model_type": "prophet",
            "training_samples": len(data)
        }

    async def _calculate_accuracy(
        self,
        company: str,
        monitor_id: Optional[str],
        forecasts: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate forecast accuracy metrics (MAE, RMSE, MAPE)."""

        accuracy = {}

        # Get actual values from recent period
        # Compare with past forecasts to calculate accuracy

        # This is a placeholder - actual implementation would:
        # 1. Retrieve forecasts made 1-3 months ago
        # 2. Compare with actual values observed
        # 3. Calculate MAE, RMSE, MAPE

        accuracy["mae"] = 0.0  # Mean Absolute Error
        accuracy["rmse"] = 0.0  # Root Mean Squared Error
        accuracy["mape"] = 0.0  # Mean Absolute Percentage Error

        return accuracy
```

### 2.2 ScenarioSimulator

**Purpose**: Run "what-if" scenario simulations

**Implementation**:
```python
# consultantos/utils/scenario_simulator.py

from typing import Dict, Any, List
from consultantos.models.forecasting import ScenarioParameters, ForecastMetric
import pandas as pd
import numpy as np
from prophet import Prophet

class ScenarioSimulator:
    """Simulate forecast scenarios with different parameters."""

    async def simulate(
        self,
        base_forecasts: Dict[str, Any],
        parameters: ScenarioParameters,
        horizon_months: int
    ) -> Dict[str, Any]:
        """Run scenario simulation with specified parameters."""

        # Apply scenario adjustments to base forecasts
        adjusted_forecasts = {}

        for metric, forecast in base_forecasts.items():
            adjusted = self._apply_scenario_adjustments(
                forecast=forecast,
                parameters=parameters,
                metric=metric
            )
            adjusted_forecasts[metric] = adjusted

        # Run Monte Carlo simulation for uncertainty quantification
        monte_carlo_results = await self._monte_carlo_simulation(
            adjusted_forecasts=adjusted_forecasts,
            parameters=parameters,
            n_simulations=1000
        )

        return {
            "scenario_name": parameters.name,
            "parameters": parameters.dict(),
            "adjusted_forecasts": adjusted_forecasts,
            "monte_carlo": monte_carlo_results,
            "confidence_level": 0.95
        }

    def _apply_scenario_adjustments(
        self,
        forecast: Dict[str, Any],
        parameters: ScenarioParameters,
        metric: str
    ) -> Dict[str, Any]:
        """Apply scenario parameters to forecast values."""

        adjusted_values = []

        for value in forecast["forecast_values"]:
            adjusted_value = value.copy()

            # Apply price change impact (affects revenue)
            if metric == ForecastMetric.REVENUE.value and parameters.price_change_pct:
                adjustment = 1 + (parameters.price_change_pct / 100)
                adjusted_value["predicted_value"] *= adjustment
                adjusted_value["lower_bound"] *= adjustment
                adjusted_value["upper_bound"] *= adjustment

            # Apply market expansion impact (affects market share, revenue)
            if metric == ForecastMetric.MARKET_SHARE.value and parameters.market_expansion_pct:
                adjustment = 1 + (parameters.market_expansion_pct / 100)
                adjusted_value["predicted_value"] *= adjustment
                adjusted_value["lower_bound"] *= adjustment
                adjusted_value["upper_bound"] *= adjustment

            # Apply competitor action impact (affects sentiment, market share)
            if parameters.competitor_action and metric == ForecastMetric.SENTIMENT.value:
                # Negative impact on sentiment
                adjustment = 0.9  # 10% decrease
                adjusted_value["predicted_value"] *= adjustment
                adjusted_value["lower_bound"] *= adjustment
                adjusted_value["upper_bound"] *= adjustment

            adjusted_values.append(adjusted_value)

        return {
            **forecast,
            "forecast_values": adjusted_values,
            "scenario_adjusted": True
        }

    async def _monte_carlo_simulation(
        self,
        adjusted_forecasts: Dict[str, Any],
        parameters: ScenarioParameters,
        n_simulations: int = 1000
    ) -> Dict[str, Any]:
        """Run Monte Carlo simulation for uncertainty quantification."""

        # Extract forecast values
        results = {}

        for metric, forecast in adjusted_forecasts.items():
            values = [v["predicted_value"] for v in forecast["forecast_values"]]
            lower = [v["lower_bound"] for v in forecast["forecast_values"]]
            upper = [v["upper_bound"] for v in forecast["forecast_values"]]

            # Simulate n_simulations trajectories
            simulations = []
            for _ in range(n_simulations):
                # Sample from normal distribution using forecast intervals
                simulation = []
                for val, lb, ub in zip(values, lower, upper):
                    std = (ub - lb) / 4  # Approximate std from 95% CI
                    sampled = np.random.normal(val, std)
                    simulation.append(sampled)
                simulations.append(simulation)

            simulations = np.array(simulations)

            # Calculate percentiles
            results[metric] = {
                "p10": np.percentile(simulations, 10, axis=0).tolist(),
                "p50": np.percentile(simulations, 50, axis=0).tolist(),
                "p90": np.percentile(simulations, 90, axis=0).tolist(),
                "mean": np.mean(simulations, axis=0).tolist(),
                "std": np.std(simulations, axis=0).tolist()
            }

        return results
```

### 2.3 Data Models

```python
# consultantos/models/forecasting.py

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ForecastMetric(str, Enum):
    """Types of metrics to forecast."""
    REVENUE = "revenue"
    MARKET_SHARE = "market_share"
    SENTIMENT = "sentiment"
    COMPETITIVE_THREAT = "competitive_threat"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    CHURN_RATE = "churn_rate"

class ForecastHorizon(str, Enum):
    """Forecast time horizons."""
    ONE_MONTH = "1m"
    THREE_MONTHS = "3m"
    SIX_MONTHS = "6m"
    TWELVE_MONTHS = "12m"

class ScenarioParameters(BaseModel):
    """Parameters for scenario simulation."""
    name: str = Field(description="Scenario name: best_case, worst_case, custom")
    price_change_pct: Optional[float] = Field(
        default=None,
        description="Price change percentage (-20 = 20% decrease)"
    )
    market_expansion_pct: Optional[float] = Field(
        default=None,
        description="Market expansion percentage (15 = 15% growth)"
    )
    competitor_action: Optional[str] = Field(
        default=None,
        description="Competitor action: new_product, price_cut, market_exit"
    )
    economic_factor: Optional[str] = Field(
        default=None,
        description="Economic factor: recession, boom, stable"
    )
    custom_adjustments: Optional[Dict[str, float]] = Field(
        default=None,
        description="Custom metric adjustments"
    )

class ForecastValue(BaseModel):
    """Single forecast data point."""
    date: str
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence_interval: float = 0.95

class ForecastRequest(BaseModel):
    """Request to generate forecast."""
    company: str
    monitor_id: Optional[str] = None
    metrics: List[ForecastMetric] = [
        ForecastMetric.REVENUE,
        ForecastMetric.MARKET_SHARE,
        ForecastMetric.SENTIMENT
    ]
    horizon_months: int = Field(default=6, ge=1, le=24)
    scenarios: Optional[List[ScenarioParameters]] = None
    include_monte_carlo: bool = Field(
        default=False,
        description="Include Monte Carlo simulation"
    )

class ForecastResponse(BaseModel):
    """Forecast generation response."""
    forecast_id: Optional[str] = None
    company: str
    monitor_id: Optional[str]
    forecasts: Dict[str, Any]  # metric -> forecast data
    scenarios: Dict[str, Any] = {}  # scenario_name -> scenario results
    accuracy_metrics: Dict[str, float] = {}
    horizon_months: int
    generated_at: datetime
    model_version: str = "prophet-1.0"

class ScenarioComparisonRequest(BaseModel):
    """Request to compare multiple scenarios."""
    forecast_id: str
    scenario_ids: List[str]
    metrics_to_compare: List[ForecastMetric]
```

### 2.4 API Endpoints

```python
# consultantos/api/forecasting_endpoints.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from consultantos.models.forecasting import (
    ForecastRequest,
    ForecastResponse,
    ScenarioComparisonRequest
)
from consultantos.agents.forecasting_agent import ForecastingAgent
from consultantos.auth import get_current_user
from consultantos.database import get_database
import uuid

router = APIRouter(prefix="/forecasting", tags=["predictive-analytics"])

@router.post("/generate", response_model=ForecastResponse)
async def generate_forecast(
    request: ForecastRequest,
    background_tasks: BackgroundTasks,
    user=Depends(get_current_user)
):
    """Generate forecast for company/monitor."""

    agent = ForecastingAgent()

    # Generate forecast
    response = await agent.execute(
        company=request.company,
        monitor_id=request.monitor_id,
        metrics=request.metrics,
        horizon_months=request.horizon_months,
        scenarios=request.scenarios
    )

    # Store forecast in database
    forecast_id = str(uuid.uuid4())
    response.forecast_id = forecast_id

    db = get_database()
    await db.collection("forecasts").document(forecast_id).set(response.dict())

    # Update monitor with latest forecast (background)
    if request.monitor_id:
        background_tasks.add_task(
            _update_monitor_forecast,
            monitor_id=request.monitor_id,
            forecast_id=forecast_id
        )

    return response

@router.get("/{forecast_id}", response_model=ForecastResponse)
async def get_forecast(
    forecast_id: str,
    user=Depends(get_current_user)
):
    """Get forecast by ID."""

    db = get_database()
    doc = await db.collection("forecasts").document(forecast_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Forecast not found")

    return ForecastResponse(**doc.to_dict())

@router.post("/scenarios", response_model=Dict[str, Any])
async def run_scenario(
    forecast_id: str,
    scenario: ScenarioParameters,
    user=Depends(get_current_user)
):
    """Run a new scenario simulation on existing forecast."""

    # Get base forecast
    db = get_database()
    doc = await db.collection("forecasts").document(forecast_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Forecast not found")

    forecast_data = doc.to_dict()

    # Run scenario
    simulator = ScenarioSimulator()
    scenario_result = await simulator.simulate(
        base_forecasts=forecast_data["forecasts"],
        parameters=scenario,
        horizon_months=forecast_data["horizon_months"]
    )

    # Store scenario
    scenario_id = str(uuid.uuid4())
    await db.collection("forecast_scenarios").document(scenario_id).set({
        "forecast_id": forecast_id,
        **scenario_result
    })

    return {
        "scenario_id": scenario_id,
        **scenario_result
    }

@router.get("/scenarios/{scenario_id}")
async def get_scenario(
    scenario_id: str,
    user=Depends(get_current_user)
):
    """Get scenario results."""

    db = get_database()
    doc = await db.collection("forecast_scenarios").document(scenario_id).get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Scenario not found")

    return doc.to_dict()

@router.get("/monitors/{monitor_id}/forecasts")
async def get_monitor_forecasts(
    monitor_id: str,
    limit: int = 10,
    user=Depends(get_current_user)
):
    """Get all forecasts for a monitor."""

    db = get_database()
    docs = await db.collection("forecasts") \
        .where("monitor_id", "==", monitor_id) \
        .order_by("generated_at", direction="DESCENDING") \
        .limit(limit) \
        .get()

    forecasts = [doc.to_dict() for doc in docs]

    return {
        "monitor_id": monitor_id,
        "forecasts": forecasts,
        "total": len(forecasts)
    }

@router.post("/compare")
async def compare_scenarios(
    request: ScenarioComparisonRequest,
    user=Depends(get_current_user)
):
    """Compare multiple scenarios side-by-side."""

    db = get_database()

    # Get all scenarios
    scenarios = []
    for scenario_id in request.scenario_ids:
        doc = await db.collection("forecast_scenarios").document(scenario_id).get()
        if doc.exists:
            scenarios.append(doc.to_dict())

    # Build comparison
    comparison = {
        "forecast_id": request.forecast_id,
        "metrics": request.metrics_to_compare,
        "scenarios": scenarios,
        "summary": _build_comparison_summary(scenarios, request.metrics_to_compare)
    }

    return comparison

@router.get("/accuracy")
async def get_forecast_accuracy(
    company: Optional[str] = None,
    metric: Optional[ForecastMetric] = None,
    user=Depends(get_current_user)
):
    """Get forecast accuracy metrics."""

    # Calculate accuracy across all forecasts
    # This would compare historical forecasts with actual observed values

    # Placeholder implementation
    return {
        "company": company,
        "metric": metric.value if metric else "all",
        "accuracy_metrics": {
            "mae": 12.5,  # Mean Absolute Error
            "rmse": 15.3,  # Root Mean Squared Error
            "mape": 8.2,  # Mean Absolute Percentage Error (%)
            "samples": 50
        },
        "trend": "improving"  # improving, stable, declining
    }

async def _update_monitor_forecast(monitor_id: str, forecast_id: str):
    """Update monitor with latest forecast (background task)."""

    db = get_database()
    await db.collection("monitors").document(monitor_id).update({
        "latest_forecast_id": forecast_id,
        "last_forecast_at": datetime.utcnow()
    })

def _build_comparison_summary(
    scenarios: List[Dict[str, Any]],
    metrics: List[ForecastMetric]
) -> Dict[str, Any]:
    """Build summary comparing scenarios."""

    # Extract final values for each scenario/metric
    summary = {}

    for metric in metrics:
        summary[metric.value] = {}

        for scenario in scenarios:
            name = scenario["scenario_name"]
            if metric.value in scenario["adjusted_forecasts"]:
                forecast = scenario["adjusted_forecasts"][metric.value]
                final_value = forecast["forecast_values"][-1]["predicted_value"]
                summary[metric.value][name] = final_value

    return summary
```

---

## Skill 3: Dark Data Mining

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Dark Data Mining System                          │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │                  Data Connectors (OAuth2)                   │    │
│  │  Gmail │ Slack │ Drive │ Confluence │ Zendesk │ Intercom   │    │
│  └────┬──────┬──────┬────────┬───────────┬─────────┬──────────┘    │
│       │      │      │        │           │         │                │
│       └──────┴──────┴────────┴───────────┴─────────┘                │
│                              │                                       │
│                              ▼                                       │
│                   ┌──────────────────────┐                          │
│                   │   DarkDataAgent      │                          │
│                   │   (Orchestrator)     │                          │
│                   └──────────┬───────────┘                          │
│                              │                                       │
│                              ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │           DarkDataProcessor (NLP Pipeline)               │       │
│  │  1. Entity Extraction (companies, people, products)      │       │
│  │  2. Relationship Mapping (company-person, co-mentions)   │       │
│  │  3. Sentiment Analysis (per-entity over time)            │       │
│  │  4. Topic Modeling (LDA / BERTopic)                      │       │
│  │  5. Trend Detection (emerging topics, sentiment shifts)  │       │
│  └─────────────────────────┬───────────────────────────────┘       │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │              PrivacyManager (GDPR Compliance)            │       │
│  │  - PII Detection & Redaction                             │       │
│  │  - Access Control (RBAC)                                 │       │
│  │  - Audit Logging                                         │       │
│  │  - Encryption (at-rest, in-transit)                      │       │
│  └─────────────────────────┬───────────────────────────────┘       │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │         DarkDataStore (Firestore)                        │       │
│  │  dark_data_sources │ dark_data_insights │ entities       │       │
│  └─────────────────────────┬───────────────────────────────┘       │
│                            │                                         │
│                            ▼                                         │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │    IntelligenceMonitor Integration                       │       │
│  │    (Dark data signals → Change detection → Alerts)       │       │
│  └─────────────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.1 DarkDataAgent

**Purpose**: Orchestrate dark data extraction and insight generation

**Implementation**:
```python
# consultantos/agents/dark_data_agent.py

from typing import Optional, List, Dict, Any
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.dark_data import (
    DarkDataSource,
    DarkDataInsight,
    ExtractionRequest,
    ExtractionResponse
)
from consultantos.utils.data_connectors import (
    DataConnectorFactory,
    DataConnector
)
from consultantos.utils.dark_data_processor import DarkDataProcessor
from consultantos.utils.privacy_manager import PrivacyManager
from consultantos.monitoring.entity_tracker import EntityTracker
from consultantos.database import get_database
from datetime import datetime, timedelta

class DarkDataAgent(BaseAgent):
    """Agent for extracting insights from dark data sources."""

    def __init__(self):
        super().__init__(agent_name="dark_data")
        self.processor = DarkDataProcessor()
        self.privacy_manager = PrivacyManager()
        self.entity_tracker = EntityTracker()
        self.db = get_database()

    async def _execute_internal(
        self,
        source_id: str,
        extraction_type: str = "incremental",  # incremental | full
        date_range: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> ExtractionResponse:
        """Extract and process dark data from source."""

        # Get source configuration
        source = await self._get_source(source_id)

        # Create appropriate connector
        connector = DataConnectorFactory.create(
            source_type=source.source_type,
            credentials=source.oauth_credentials
        )

        # Determine date range for extraction
        if extraction_type == "incremental":
            start_date = source.last_processed_timestamp or (datetime.utcnow() - timedelta(days=30))
            end_date = datetime.utcnow()
        else:
            # Full extraction
            start_date = date_range.get("start") if date_range else (datetime.utcnow() - timedelta(days=365))
            end_date = date_range.get("end") if date_range else datetime.utcnow()

        # Extract documents
        documents = await connector.extract(
            start_date=start_date,
            end_date=end_date,
            filters=kwargs.get("filters", {})
        )

        # Process documents in batches
        insights = []
        entities_found = []
        documents_processed = 0

        for batch in self._batch_documents(documents, batch_size=50):
            # Apply privacy controls (PII redaction)
            sanitized_batch = await self.privacy_manager.sanitize_batch(batch)

            # Process with NLP
            batch_insights = await self.processor.process_batch(sanitized_batch)

            # Extract entities
            batch_entities = await self.processor.extract_entities(sanitized_batch)

            # Store insights
            for insight in batch_insights:
                await self._store_insight(source_id, insight)
                insights.append(insight)

            # Update entity tracker
            for entity in batch_entities:
                await self.entity_tracker.update_entity(entity)
                entities_found.append(entity)

            documents_processed += len(batch)

        # Update source metadata
        await self._update_source(
            source_id=source_id,
            last_processed_timestamp=end_date,
            documents_processed=documents_processed
        )

        # Generate insights summary
        insights_summary = await self._generate_insights_summary(insights)

        return ExtractionResponse(
            source_id=source_id,
            documents_processed=documents_processed,
            insights_generated=len(insights),
            entities_found=len(entities_found),
            insights_summary=insights_summary,
            processed_at=datetime.utcnow()
        )

    async def _get_source(self, source_id: str) -> DarkDataSource:
        """Get source configuration from database."""

        doc = await self.db.collection("dark_data_sources").document(source_id).get()

        if not doc.exists:
            raise ValueError(f"Source {source_id} not found")

        return DarkDataSource(**doc.to_dict())

    async def _store_insight(self, source_id: str, insight: DarkDataInsight):
        """Store insight in database."""

        await self.db.collection("dark_data_insights").add(insight.dict())

    async def _update_source(
        self,
        source_id: str,
        last_processed_timestamp: datetime,
        documents_processed: int
    ):
        """Update source processing metadata."""

        await self.db.collection("dark_data_sources").document(source_id).update({
            "last_processed_timestamp": last_processed_timestamp,
            "total_documents_processed": firestore.Increment(documents_processed),
            "updated_at": datetime.utcnow()
        })

    async def _generate_insights_summary(
        self,
        insights: List[DarkDataInsight]
    ) -> Dict[str, Any]:
        """Generate summary of extracted insights."""

        # Group by insight type
        by_type = {}
        for insight in insights:
            if insight.insight_type not in by_type:
                by_type[insight.insight_type] = []
            by_type[insight.insight_type].append(insight)

        # Extract top trends
        trends = [
            i for i in insights
            if i.insight_type == "trend"
        ][:5]

        # Extract top relationships
        relationships = [
            i for i in insights
            if i.insight_type == "relationship"
        ][:5]

        return {
            "total_insights": len(insights),
            "by_type": {k: len(v) for k, v in by_type.items()},
            "top_trends": [t.dict() for t in trends],
            "top_relationships": [r.dict() for r in relationships]
        }

    def _batch_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 50
    ) -> List[List[Dict[str, Any]]]:
        """Split documents into batches."""

        batches = []
        for i in range(0, len(documents), batch_size):
            batches.append(documents[i:i + batch_size])

        return batches
```

### 3.2 Data Connectors

**Purpose**: Plugin architecture for connecting to external data sources

**Implementation**:
```python
# consultantos/utils/data_connectors.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import os

class DataConnector(ABC):
    """Base interface for data source connectors."""

    @abstractmethod
    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """Establish connection to data source."""
        pass

    @abstractmethod
    async def extract(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract documents from source."""
        pass

    @abstractmethod
    async def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform raw data to standard format."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection to data source."""
        pass

class GmailConnector(DataConnector):
    """Connector for Gmail API."""

    def __init__(self):
        self.service = None

    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to Gmail API using OAuth2 credentials."""

        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        # Build credentials from stored OAuth tokens
        creds = Credentials(
            token=credentials["access_token"],
            refresh_token=credentials.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=os.getenv("GMAIL_CLIENT_ID"),
            client_secret=os.getenv("GMAIL_CLIENT_SECRET")
        )

        self.service = build('gmail', 'v1', credentials=creds)
        return True

    async def extract(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract emails from Gmail."""

        # Build query
        query_parts = []
        query_parts.append(f"after:{start_date.strftime('%Y/%m/%d')}")
        query_parts.append(f"before:{end_date.strftime('%Y/%m/%d')}")

        if filters.get("from"):
            query_parts.append(f"from:{filters['from']}")

        if filters.get("subject"):
            query_parts.append(f"subject:{filters['subject']}")

        query = " ".join(query_parts)

        # List messages
        results = self.service.users().messages().list(
            userId='me',
            q=query,
            maxResults=1000
        ).execute()

        messages = results.get('messages', [])

        # Get full message content
        documents = []
        for msg in messages:
            msg_data = self.service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='full'
            ).execute()

            documents.append(await self.transform(msg_data))

        return documents

    async def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Gmail message to standard format."""

        # Extract headers
        headers = {h['name']: h['value'] for h in raw_data['payload']['headers']}

        # Extract body
        body = ""
        if 'parts' in raw_data['payload']:
            for part in raw_data['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    import base64
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break

        return {
            "source_type": "gmail",
            "document_id": raw_data['id'],
            "timestamp": datetime.fromtimestamp(int(raw_data['internalDate']) / 1000),
            "from": headers.get('From'),
            "to": headers.get('To'),
            "subject": headers.get('Subject'),
            "body": body,
            "metadata": {
                "thread_id": raw_data['threadId'],
                "labels": raw_data.get('labelIds', [])
            }
        }

    async def disconnect(self):
        """Close Gmail connection."""
        self.service = None

class SlackConnector(DataConnector):
    """Connector for Slack API."""

    def __init__(self):
        self.client = None

    async def connect(self, credentials: Dict[str, Any]) -> bool:
        """Connect to Slack API using OAuth2 credentials."""

        from slack_sdk import WebClient

        self.client = WebClient(token=credentials["access_token"])
        return True

    async def extract(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract messages from Slack."""

        # Get channels
        channels = filters.get("channels", [])

        documents = []

        for channel_id in channels:
            # Get channel history
            response = self.client.conversations_history(
                channel=channel_id,
                oldest=str(int(start_date.timestamp())),
                latest=str(int(end_date.timestamp())),
                limit=1000
            )

            for msg in response['messages']:
                documents.append(await self.transform(msg))

        return documents

    async def transform(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Slack message to standard format."""

        return {
            "source_type": "slack",
            "document_id": raw_data.get('ts'),
            "timestamp": datetime.fromtimestamp(float(raw_data['ts'])),
            "user": raw_data.get('user'),
            "channel": raw_data.get('channel'),
            "text": raw_data.get('text'),
            "metadata": {
                "type": raw_data.get('type'),
                "subtype": raw_data.get('subtype'),
                "thread_ts": raw_data.get('thread_ts')
            }
        }

    async def disconnect(self):
        """Close Slack connection."""
        self.client = None

# Similar implementations for DriveConnector, ConfluenceConnector, ZendeskConnector...

class DataConnectorFactory:
    """Factory for creating data connectors."""

    @staticmethod
    def create(source_type: str, credentials: Dict[str, Any]) -> DataConnector:
        """Create appropriate connector based on source type."""

        connectors = {
            "gmail": GmailConnector,
            "slack": SlackConnector,
            # "drive": DriveConnector,
            # "confluence": ConfluenceConnector,
            # "zendesk": ZendeskConnector,
        }

        if source_type not in connectors:
            raise ValueError(f"Unsupported source type: {source_type}")

        connector = connectors[source_type]()
        return connector
```

Due to length limits, I'll create the complete architecture document now and include all remaining sections.

Let me write the complete architecture document to the file:


---

## API Design

### Complete API Endpoint Summary

#### Conversational AI Endpoints (`/chat`)

| Method | Endpoint | Purpose | Request Model | Response Model | Rate Limit |
|--------|----------|---------|---------------|----------------|------------|
| POST | `/chat/conversations` | Create new conversation | `ConversationCreate` | `{conversation_id, created_at}` | 20/hour |
| POST | `/chat/conversations/{id}/messages` | Send message | `ConversationMessage` | `ConversationResponse` or SSE | 100/hour |
| GET | `/chat/conversations/{id}` | Get conversation history | - | `ConversationContext` | 100/hour |
| GET | `/chat/conversations` | List user conversations | `?limit, ?offset` | `{conversations[], total}` | 100/hour |
| DELETE | `/chat/conversations/{id}` | Delete conversation | - | `{status: deleted}` | 100/hour |
| POST | `/chat/rag/index` | Index report for RAG | `{report_id}` | `{job_id}` | 100/hour |
| GET | `/chat/suggestions` | Get query suggestions | `?query` | `{suggestions[]}` | 100/hour |

#### Predictive Analytics Endpoints (`/forecasting`)

| Method | Endpoint | Purpose | Request Model | Response Model | Rate Limit |
|--------|----------|---------|---------------|----------------|------------|
| POST | `/forecasting/generate` | Generate forecast | `ForecastRequest` | `ForecastResponse` | 20/hour |
| GET | `/forecasting/{forecast_id}` | Get forecast | - | `ForecastResponse` | 100/hour |
| POST | `/forecasting/scenarios` | Run scenario | `ScenarioParameters` | `{scenario_id, results}` | 20/hour |
| GET | `/forecasting/scenarios/{id}` | Get scenario results | - | `{scenario data}` | 100/hour |
| GET | `/forecasting/monitors/{id}/forecasts` | Get monitor forecasts | `?limit` | `{forecasts[]}` | 100/hour |
| POST | `/forecasting/compare` | Compare scenarios | `ScenarioComparisonRequest` | `{comparison}` | 20/hour |
| GET | `/forecasting/accuracy` | Get accuracy metrics | `?company, ?metric` | `{accuracy_metrics}` | 100/hour |

#### Dark Data Mining Endpoints (`/dark-data`)

| Method | Endpoint | Purpose | Request Model | Response Model | Rate Limit |
|--------|----------|---------|---------------|----------------|------------|
| POST | `/dark-data/sources` | Connect new source | `SourceConnectRequest` | `{source_id, oauth_url}` | 10/day |
| GET | `/dark-data/sources` | List connected sources | - | `{sources[]}` | 100/hour |
| DELETE | `/dark-data/sources/{id}` | Disconnect source | - | `{status: disconnected}` | 10/day |
| POST | `/dark-data/extract` | Trigger extraction job | `ExtractionRequest` | `{job_id}` | 10/day |
| GET | `/dark-data/insights` | Query insights | `?source, ?type, ?limit` | `{insights[]}` | 100/hour |
| GET | `/dark-data/entities` | Get entity relationships | `?entity_type, ?entity_name` | `{entities[], relationships[]}` | 100/hour |
| GET | `/dark-data/trends` | Get trending topics | `?timeframe, ?source` | `{trends[]}` | 100/hour |
| GET | `/dark-data/jobs/{job_id}` | Get job status | - | `{status, progress, results}` | 100/hour |
| POST | `/dark-data/privacy/redact` | Manual PII redaction | `{document_id}` | `{redacted_content}` | 20/hour |

### Error Handling Strategy

**Standard Error Response Format**:
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable error message",
    "details": {
      "field": "company",
      "issue": "Required field missing"
    },
    "request_id": "req_abc123"
  }
}
```

**Error Codes**:
- `INVALID_REQUEST` (400): Malformed request, validation errors
- `UNAUTHORIZED` (401): Missing or invalid API key
- `FORBIDDEN` (403): Access denied (RBAC)
- `NOT_FOUND` (404): Resource not found
- `RATE_LIMIT_EXCEEDED` (429): Too many requests
- `INTERNAL_ERROR` (500): Server error
- `SERVICE_UNAVAILABLE` (503): Temporary service disruption
- `TIMEOUT` (504): Request timeout (>30s)

**Retry Logic**:
- Exponential backoff: 1s, 2s, 4s, 8s, 16s
- Retry on: 429, 500, 503, 504
- Do not retry on: 400, 401, 403, 404
- Max retries: 3

---

## Database Schema

### Firestore Collections

#### 1. `conversations`
```typescript
{
  conversation_id: string (document ID)
  user_id: string (indexed)
  created_at: timestamp (indexed)
  updated_at: timestamp
  title: string (auto-generated from first query)
  message_count: number
  last_message_preview: string (max 200 chars)
  context_summary: string (for long conversations)
  status: "active" | "archived" | "deleted"
}

// Indexes
composite: (user_id, created_at DESC)
```

#### 2. `conversation_messages` (subcollection of `conversations`)
```typescript
{
  message_id: string (document ID)
  conversation_id: string (parent reference)
  role: "user" | "assistant" | "system"
  content: string
  timestamp: timestamp (indexed)
  metadata: {
    query_type: string (comparison | trend | forecast | explain | deep_dive)
    agents_used: string[] (research, market, financial, framework, synthesis)
    response_time: number (seconds)
    tokens_used: number
    rag_documents_used: number
    confidence_score: number (0-1)
  }
}

// Indexes
composite: (conversation_id, timestamp ASC)
```

#### 3. `rag_documents`
```typescript
{
  document_id: string (document ID)
  report_id: string (indexed, link to existing reports)
  chunk_index: number
  chunk_text: string
  embedding_vector: number[] (768-dim for Gemini)
  metadata: {
    company: string (indexed)
    industry: string (indexed)
    frameworks: string[]
    created_at: timestamp
    confidence_score: number
  }
  indexed_at: timestamp
}

// Indexes
composite: (report_id, chunk_index)
composite: (metadata.company, indexed_at DESC)
// Vector index (requires Firestore vector search or external vector DB)
```

#### 4. `forecasts`
```typescript
{
  forecast_id: string (document ID)
  monitor_id: string (indexed, nullable)
  company: string (indexed)
  industry: string
  metrics: string[] (revenue, market_share, sentiment, competitive_threat)
  horizon_months: number (1-24)
  forecasts: {
    [metric: string]: {
      metric: string
      forecast_values: Array<{
        date: string (ISO 8601)
        predicted_value: number
        lower_bound: number
        upper_bound: number
        confidence_interval: number (0.95)
      }>
      model_type: "prophet" | "arima" | "ets"
      training_samples: number
    }
  }
  scenarios: string[] (scenario_ids)
  accuracy_metrics: {
    mae: number
    rmse: number
    mape: number
  }
  generated_at: timestamp (indexed)
  model_version: string
}

// Indexes
composite: (monitor_id, generated_at DESC)
composite: (company, generated_at DESC)
```

#### 5. `forecast_scenarios`
```typescript
{
  scenario_id: string (document ID)
  forecast_id: string (indexed, parent reference)
  scenario_name: string (best_case | worst_case | custom)
  parameters: {
    price_change_pct: number (nullable)
    market_expansion_pct: number (nullable)
    competitor_action: string (nullable)
    economic_factor: string (nullable)
    custom_adjustments: { [metric: string]: number }
  }
  adjusted_forecasts: {
    [metric: string]: {
      metric: string
      forecast_values: Array<{...}>
      scenario_adjusted: boolean
    }
  }
  monte_carlo: {
    [metric: string]: {
      p10: number[]
      p50: number[]
      p90: number[]
      mean: number[]
      std: number[]
    }
  }
  confidence_level: number (0.95)
  created_at: timestamp
}

// Indexes
composite: (forecast_id, created_at DESC)
```

#### 6. `dark_data_sources`
```typescript
{
  source_id: string (document ID)
  user_id: string (indexed)
  source_type: "gmail" | "slack" | "drive" | "confluence" | "zendesk" | "intercom"
  connection_status: "connected" | "disconnected" | "error" | "pending"
  oauth_credentials: {
    access_token: string (encrypted)
    refresh_token: string (encrypted)
    expires_at: timestamp
    scope: string[]
  }
  filters: {
    channels: string[] (for Slack)
    folders: string[] (for Drive)
    spaces: string[] (for Confluence)
  }
  last_processed_timestamp: timestamp (nullable)
  total_documents_processed: number
  created_at: timestamp
  updated_at: timestamp
  error_message: string (nullable)
}

// Indexes
composite: (user_id, source_type)
composite: (user_id, updated_at DESC)
```

#### 7. `dark_data_insights`
```typescript
{
  insight_id: string (document ID)
  source_id: string (indexed)
  insight_type: "trend" | "relationship" | "sentiment_shift" | "emerging_topic" | "competitive_mention"
  content: string (insight description)
  entities: Array<{
    entity_type: "company" | "person" | "product" | "technology"
    entity_name: string
    confidence: number (0-1)
  }>
  metadata: {
    source_documents: string[] (document IDs)
    confidence: number (0-1)
    timeframe: {
      start: timestamp
      end: timestamp
    }
    sentiment_score: number (-1 to 1, nullable)
  }
  created_at: timestamp (indexed)
  alert_triggered: boolean (has this triggered an alert?)
}

// Indexes
composite: (source_id, created_at DESC)
composite: (insight_type, created_at DESC)
composite: (alert_triggered, created_at DESC)
```

#### 8. `dark_data_entities`
```typescript
{
  entity_id: string (document ID)
  entity_type: "company" | "person" | "product" | "technology"
  entity_name: string (indexed)
  relationships: Array<{
    related_entity_id: string
    relationship_type: "works_at" | "competes_with" | "partners_with" | "mentions"
    confidence: number (0-1)
    first_seen: timestamp
    last_seen: timestamp
  }>
  mentions_count: number
  sentiment_score: number (-1 to 1, avg across all mentions)
  sentiment_trend: "increasing" | "decreasing" | "stable"
  first_seen: timestamp (indexed)
  last_seen: timestamp (indexed)
  metadata: {
    sources: string[] (source_ids where mentioned)
    aliases: string[] (alternative names)
  }
}

// Indexes
composite: (entity_type, entity_name)
composite: (entity_type, mentions_count DESC)
composite: (entity_type, last_seen DESC)
```

### Database Migration Strategy

**Phase 1: Schema Creation**
```bash
# Create new collections with indexes
firebase firestore:indexes:deploy firestore.indexes.json

# Collections to create:
# - conversations
# - conversation_messages (subcollection)
# - rag_documents
# - forecasts
# - forecast_scenarios
# - dark_data_sources
# - dark_data_insights
# - dark_data_entities
```

**Phase 2: Data Backfill** (if needed)
```python
# Backfill RAG documents from existing reports
# Script: scripts/backfill_rag_documents.py

async def backfill_rag_documents():
    db = get_database()
    rag_system = RAGSystem()

    # Get all existing reports
    reports = await db.collection("reports").get()

    for report_doc in reports:
        report = report_doc.to_dict()

        # Index report content
        await rag_system.index_report(
            report_id=report_doc.id,
            report_content=report.get("full_content", ""),
            metadata={
                "company": report["company"],
                "industry": report["industry"],
                "frameworks": report.get("frameworks", []),
                "created_at": report["created_at"]
            }
        )

        print(f"Indexed report {report_doc.id}")
```

**Phase 3: Monitoring Integration**
```python
# Extend MonitorAnalysisSnapshot with forecast fields
# Script: scripts/migrate_monitor_snapshots.py

async def extend_monitor_snapshots():
    db = get_database()

    snapshots = await db.collection("monitor_analysis_snapshots").get()

    for snapshot_doc in snapshots:
        # Add new fields
        await snapshot_doc.reference.update({
            "forecast_data": {},  # Will be populated by ForecastingAgent
            "dark_data_signals": [],  # Will be populated by DarkDataAgent
            "updated_at": firestore.SERVER_TIMESTAMP
        })
```

---

## Caching Strategy

### Multi-Layer Caching Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Cache Hierarchy                               │
│                                                                      │
│  Layer 1: In-Memory Cache (Redis/Python dict)                       │
│  - Recent conversations (100 per user, TTL: 1 hour)                 │
│  - Recent forecasts (50, TTL: 24 hours)                             │
│  - Recent insights (100, TTL: 6 hours)                              │
│  - Response time: <10ms                                             │
│                                                                      │
│  Layer 2: Disk Cache (diskcache)                                    │
│  - Conversation embeddings (TTL: 7 days)                            │
│  - Forecast models (TTL: 7 days)                                    │
│  - Entity embeddings (TTL: 30 days)                                 │
│  - Response time: <100ms                                            │
│                                                                      │
│  Layer 3: Database Cache (Firestore)                                │
│  - Forecast results (TTL: 24 hours)                                 │
│  - Processed documents (never invalidate, append-only)              │
│  - Response time: <500ms                                            │
│                                                                      │
│  Layer 4: Semantic Cache (cosine similarity)                        │
│  - Similar query responses (similarity > 0.9, TTL: 24 hours)        │
│  - Response time: <200ms                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### Cache Invalidation Rules

#### Conversational AI
```python
# Cache Keys
cache_key_conversation = f"conversation:{conversation_id}"
cache_key_query = f"query:{query_hash}"
cache_key_rag = f"rag:{report_id}:{chunk_index}"
cache_key_embedding = f"embedding:{text_hash}"

# Invalidation Triggers
- New message in conversation → invalidate conversation cache
- New report indexed → invalidate RAG cache for that report
- User deletes conversation → invalidate all conversation caches
- Query embedding → cache for 24 hours (never invalidate)

# TTL Policies
- Conversation context: 1 hour (refresh on activity)
- RAG embeddings: 7 days (stable)
- Similar queries: 24 hours (recompute daily)
- Query embeddings: 24 hours (recompute daily)
```

#### Predictive Analytics
```python
# Cache Keys
cache_key_forecast = f"forecast:{company}:{metric}:{horizon}"
cache_key_scenario = f"scenario:{forecast_id}:{params_hash}"
cache_key_model = f"model:prophet:{company}:{metric}"
cache_key_timeseries = f"timeseries:{monitor_id}:{metric}"

# Invalidation Triggers
- New monitoring snapshot → invalidate related forecasts
- Forecast model retrained → invalidate all forecasts using that model
- Scenario parameters changed → recompute scenario
- Historical data updated → invalidate timeseries cache

# TTL Policies
- Forecast results: 24 hours (refresh daily)
- Prophet models: 7 days (retrain weekly)
- Scenario simulations: 7 days (stable for same parameters)
- Historical timeseries: 6 hours (refresh when new data arrives)
```

#### Dark Data Mining
```python
# Cache Keys
cache_key_insight = f"insight:{source_id}:{insight_type}"
cache_key_entity = f"entity:{entity_type}:{entity_name}"
cache_key_processed = f"processed:{source_id}:{document_id}"
cache_key_nlp = f"nlp:{document_id}:{processor_version}"

# Invalidation Triggers
- New documents extracted → invalidate source insights cache
- Entity mentioned in new document → update entity cache
- NLP model updated → invalidate all NLP caches
- Document processed → never invalidate (append-only)

# TTL Policies
- Recent insights: 6 hours (refresh frequently)
- Entity embeddings: 30 days (stable)
- Processed documents: never (append-only, never invalidate)
- NLP results: 30 days (recompute on model update)
```

### Cache Performance Optimization

**Cache Warming**:
```python
# Warm cache on application startup
async def warm_cache():
    # Pre-load popular forecasts
    await _warm_forecast_cache()

    # Pre-load common entities
    await _warm_entity_cache()

    # Pre-load RAG embeddings for recent reports
    await _warm_rag_cache()

async def _warm_forecast_cache():
    # Get top 10 most accessed companies
    popular_companies = await get_popular_companies(limit=10)

    for company in popular_companies:
        # Pre-generate 6-month forecast
        await forecasting_agent.execute(
            company=company,
            horizon_months=6,
            metrics=[ForecastMetric.REVENUE, ForecastMetric.MARKET_SHARE]
        )
```

**Cache Hit Rate Monitoring**:
```python
# Track cache performance
cache_metrics = {
    "conversation_hits": 0,
    "conversation_misses": 0,
    "forecast_hits": 0,
    "forecast_misses": 0,
    "entity_hits": 0,
    "entity_misses": 0
}

def get_cache_hit_rate(cache_type: str) -> float:
    hits = cache_metrics[f"{cache_type}_hits"]
    misses = cache_metrics[f"{cache_type}_misses"]

    if hits + misses == 0:
        return 0.0

    return hits / (hits + misses)

# Target: >60% hit rate for conversational, >80% for forecasts
```

---

## Performance Targets

### Response Time SLAs

| Skill | Operation | p50 | p95 | p99 | Timeout |
|-------|-----------|-----|-----|-----|---------|
| **Conversational AI** | | | | | |
| | Query parsing | 200ms | 500ms | 1s | 5s |
| | RAG retrieval | 300ms | 1s | 2s | 5s |
| | Agent execution | 1s | 3s | 5s | 10s |
| | Response generation | 500ms | 2s | 4s | 10s |
| | **Total (non-streaming)** | **2s** | **5s** | **8s** | **30s** |
| | Streaming (first token) | 300ms | 1s | 2s | 5s |
| | RAG indexing | 5s | 15s | 30s | 60s |
| **Predictive Analytics** | | | | | |
| | Historical data retrieval | 500ms | 2s | 4s | 10s |
| | Forecast generation (6m) | 3s | 10s | 15s | 30s |
| | Scenario simulation | 5s | 15s | 25s | 60s |
| | Monte Carlo (1000 runs) | 2s | 5s | 10s | 30s |
| | Model training (weekly) | 1m | 5m | 10m | 30m |
| **Dark Data Mining** | | | | | |
| | Data extraction (100 docs) | 10s | 30s | 60s | 120s |
| | Entity extraction (per doc) | 500ms | 2s | 4s | 10s |
| | Insight generation (50 docs) | 3s | 10s | 20s | 60s |
| | Incremental processing | 1m | 5m | 10m | 30m |
| | PII detection | 100ms | 500ms | 1s | 5s |

### Throughput Requirements

| Skill | Metric | Target | Peak |
|-------|--------|--------|------|
| **Conversational AI** | | | |
| | Concurrent conversations | 50 | 100 |
| | Messages/second | 10 | 20 |
| | RAG queries/second | 5 | 10 |
| | Documents indexed/hour | 100 | 500 |
| **Predictive Analytics** | | | |
| | Forecasts generated/hour | 20 | 50 |
| | Scenarios simulated/hour | 10 | 30 |
| | Concurrent forecast requests | 5 | 10 |
| **Dark Data Mining** | | | |
| | Documents processed/hour | 5,000 | 10,000 |
| | Extraction jobs/day | 50 | 100 |
| | Entities tracked | 10,000 | 50,000 |
| | Insights generated/hour | 100 | 500 |

### Resource Usage Estimates

**Conversational AI**:
- CPU: 1 vCPU per 20 concurrent conversations
- Memory: 2GB per instance (conversation cache + embeddings)
- Storage: 100MB per 1,000 conversations
- Network: 50KB per query (avg)
- LLM tokens: 2,000 tokens/query (avg)

**Predictive Analytics**:
- CPU: 2 vCPUs per instance (Prophet is CPU-intensive)
- Memory: 4GB per instance (models + historical data)
- Storage: 50MB per 100 forecasts
- Network: 20KB per forecast request
- Computation: 10 CPU-seconds per forecast

**Dark Data Mining**:
- CPU: 2 vCPUs per instance (NLP processing)
- Memory: 3GB per instance (NLP models + entity cache)
- Storage: 500MB per 10,000 documents
- Network: 100KB per document (avg)
- API calls: 1 external API call per document

### Scaling Strategy

**Horizontal Scaling Triggers**:
- CPU usage > 70% for 5 minutes → scale up
- Memory usage > 80% for 5 minutes → scale up
- Request latency p95 > 2x SLA for 5 minutes → scale up
- Queue depth > 100 requests → scale up

**Scaling Limits**:
- Conversational AI: 1-10 instances
- Predictive Analytics: 1-5 instances
- Dark Data Mining: 1-5 instances
- Auto-scale based on Cloud Run metrics

---

## Security & Privacy

### Authentication & Authorization

**API Key Authentication** (existing):
```python
# All new endpoints use existing auth.py
from consultantos.auth import get_current_user

@router.post("/chat/conversations")
async def create_conversation(
    request: ConversationCreate,
    user=Depends(get_current_user)  # Existing auth
):
    # Validate user has permission
    pass
```

**OAuth2 for Data Connectors**:
```python
# OAuth2 flow for Gmail, Slack, Drive, etc.

# Step 1: Initiate OAuth flow
@router.post("/dark-data/sources/connect/{source_type}")
async def connect_source(source_type: str, user=Depends(get_current_user)):
    # Generate OAuth URL
    oauth_url = generate_oauth_url(
        source_type=source_type,
        user_id=user.user_id,
        redirect_uri="https://consultantos.com/oauth/callback"
    )

    return {"oauth_url": oauth_url}

# Step 2: OAuth callback
@router.get("/oauth/callback")
async def oauth_callback(code: str, state: str):
    # Exchange code for tokens
    tokens = exchange_code_for_tokens(code)

    # Store encrypted tokens
    await store_oauth_tokens(
        user_id=extract_user_from_state(state),
        tokens=encrypt_tokens(tokens)
    )

    return {"status": "connected"}
```

**Role-Based Access Control (RBAC)**:
```python
# Roles for dark data access
class Role(str, Enum):
    ADMIN = "admin"  # Full access to all dark data
    ANALYST = "analyst"  # Read access to insights, limited PII access
    VIEWER = "viewer"  # Read access to aggregated insights only

# Permission checks
def require_role(required_role: Role):
    def decorator(func):
        async def wrapper(*args, user=None, **kwargs):
            if user.role not in [required_role, Role.ADMIN]:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, user=user, **kwargs)
        return wrapper
    return decorator

@router.get("/dark-data/insights")
@require_role(Role.ANALYST)
async def get_insights(user=Depends(get_current_user)):
    # Only analysts and admins can access raw insights
    pass
```

### Data Privacy (GDPR Compliance)

**PII Detection & Redaction**:
```python
# consultantos/utils/privacy_manager.py

import re
from typing import List, Dict, Any

class PrivacyManager:
    """GDPR-compliant privacy management."""

    # PII patterns
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b',
        "ssn": r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b',
        "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        "ip_address": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    }

    async def sanitize_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sanitize batch of documents (PII redaction)."""

        sanitized = []

        for doc in documents:
            sanitized_doc = await self.redact_pii(doc)
            sanitized.append(sanitized_doc)

        return sanitized

    async def redact_pii(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Redact PII from document."""

        content = document.get("body") or document.get("text", "")

        # Redact emails
        content = re.sub(
            self.PII_PATTERNS["email"],
            "[EMAIL_REDACTED]",
            content
        )

        # Redact phone numbers
        content = re.sub(
            self.PII_PATTERNS["phone"],
            "[PHONE_REDACTED]",
            content
        )

        # Redact SSNs
        content = re.sub(
            self.PII_PATTERNS["ssn"],
            "[SSN_REDACTED]",
            content
        )

        # Redact credit cards
        content = re.sub(
            self.PII_PATTERNS["credit_card"],
            "[CC_REDACTED]",
            content
        )

        # Update document
        if "body" in document:
            document["body"] = content
        elif "text" in document:
            document["text"] = content

        return document

    async def handle_deletion_request(self, user_id: str):
        """Handle GDPR right-to-delete request."""

        db = get_database()

        # Delete all user conversations
        conversations = await db.collection("conversations") \
            .where("user_id", "==", user_id).get()

        for conv in conversations:
            await conv.reference.delete()

        # Delete all user dark data sources
        sources = await db.collection("dark_data_sources") \
            .where("user_id", "==", user_id).get()

        for source in sources:
            await source.reference.delete()

        # Anonymize any remaining user data
        # (e.g., replace user_id with anonymous hash)
```

**Data Minimization**:
```python
# Only extract necessary fields from sources
def extract_minimal_data(raw_document: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only necessary fields for analysis."""

    return {
        "document_id": raw_document["id"],
        "timestamp": raw_document["timestamp"],
        "from": raw_document.get("from", "unknown"),  # For context, will be redacted
        "subject": raw_document.get("subject", ""),
        "body": raw_document.get("body", ""),  # Will be PII-redacted
        # Exclude: attachments, full headers, recipients list, etc.
    }
```

**Encryption**:
```python
# Encrypt OAuth tokens before storage
from cryptography.fernet import Fernet
import os

# Load encryption key from Secret Manager
ENCRYPTION_KEY = os.getenv("OAUTH_ENCRYPTION_KEY")
cipher = Fernet(ENCRYPTION_KEY)

def encrypt_tokens(tokens: Dict[str, str]) -> Dict[str, str]:
    """Encrypt OAuth tokens."""

    return {
        "access_token": cipher.encrypt(tokens["access_token"].encode()).decode(),
        "refresh_token": cipher.encrypt(tokens["refresh_token"].encode()).decode(),
        "expires_at": tokens["expires_at"]
    }

def decrypt_tokens(encrypted_tokens: Dict[str, str]) -> Dict[str, str]:
    """Decrypt OAuth tokens."""

    return {
        "access_token": cipher.decrypt(encrypted_tokens["access_token"].encode()).decode(),
        "refresh_token": cipher.decrypt(encrypted_tokens["refresh_token"].encode()).decode(),
        "expires_at": encrypted_tokens["expires_at"]
    }
```

### Rate Limiting

**Existing Rate Limiting** (via slowapi):
```python
# Extend existing rate limiting in consultantos/api/main.py

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# New rate limits for Phase 1 skills
@limiter.limit("100/hour")  # Conversational AI
@router.post("/chat/conversations/{id}/messages")
async def send_message(...):
    pass

@limiter.limit("20/hour")  # Predictive Analytics (expensive)
@router.post("/forecasting/generate")
async def generate_forecast(...):
    pass

@limiter.limit("10/day")  # Dark Data Mining (quota limits)
@router.post("/dark-data/extract")
async def trigger_extraction(...):
    pass
```

### Input Validation & Sanitization

**Prevent Prompt Injection**:
```python
def sanitize_for_llm(user_input: str) -> str:
    """Sanitize user input before passing to LLM."""

    # Remove potentially harmful instructions
    harmful_patterns = [
        "ignore previous instructions",
        "disregard all prior",
        "forget everything",
        "you are now",
        "pretend you are"
    ]

    sanitized = user_input
    for pattern in harmful_patterns:
        sanitized = sanitized.replace(pattern, "[REDACTED]")

    # Escape special characters
    sanitized = sanitized.replace("{", "{{").replace("}", "}}")

    return sanitized
```

**Prevent SQL Injection** (using Firestore ORM):
```python
# Firestore queries are safe by default (no SQL injection)
# Always use parameterized queries, never string concatenation

# SAFE
await db.collection("forecasts").where("company", "==", company).get()

# NEVER DO THIS
# await db.collection("forecasts").where(f"company == '{company}'").get()
```

### Audit Logging

```python
# consultantos/utils/audit_logger.py

import logging
from datetime import datetime

audit_logger = logging.getLogger("audit")

async def log_dark_data_access(
    user_id: str,
    source_id: str,
    action: str,
    document_ids: List[str]
):
    """Log all dark data access for compliance."""

    audit_logger.info({
        "event": "dark_data_access",
        "user_id": user_id,
        "source_id": source_id,
        "action": action,  # read, extract, delete
        "document_ids": document_ids,
        "timestamp": datetime.utcnow().isoformat(),
        "ip_address": request.client.host if request else "unknown"
    })

async def log_forecast_request(
    user_id: str,
    company: str,
    horizon_months: int
):
    """Log forecast requests."""

    audit_logger.info({
        "event": "forecast_request",
        "user_id": user_id,
        "company": company,
        "horizon_months": horizon_months,
        "timestamp": datetime.utcnow().isoformat()
    })

# Retention: 90 days in Cloud Logging
```

---

## Testing Strategy

### Unit Tests

**Conversational AI Tests**:
```python
# tests/test_conversational_agent.py

import pytest
from consultantos.agents.conversational_agent import ConversationalAgent
from consultantos.models.conversational import ConversationQuery, QueryIntent

@pytest.mark.asyncio
async def test_parse_query_comparison(mock_gemini_client):
    """Test query parsing for comparison intent."""

    agent = ConversationalAgent()
    agent.client = mock_gemini_client

    query = "Compare Tesla vs BYD market share"

    parsed = await agent._parse_query(query, context=None)

    assert parsed.intent == QueryIntent.COMPARISON
    assert "Tesla" in str(parsed.entities.values())
    assert "BYD" in str(parsed.entities.values())
    assert "market_share" in str(parsed.entities.values())

@pytest.mark.asyncio
async def test_rag_retrieval(mock_rag_system):
    """Test RAG context retrieval."""

    rag_system = mock_rag_system

    results = await rag_system.retrieve_relevant_context(
        query="Tesla revenue trends",
        company="Tesla",
        top_k=3
    )

    assert len(results) == 3
    assert all(r["similarity"] > 0.5 for r in results)

@pytest.mark.asyncio
async def test_conversation_state_management():
    """Test multi-turn conversation state."""

    state_manager = ConversationStateManager()

    conv_id = await state_manager.create_conversation(user_id="test_user")

    await state_manager.save_message(
        conversation_id=conv_id,
        user_id="test_user",
        role="user",
        content="What is Tesla's market position?"
    )

    context = await state_manager.load_context(
        conversation_id=conv_id,
        user_id="test_user"
    )

    assert len(context.messages) == 1
    assert context.messages[0]["content"] == "What is Tesla's market position?"
```

**Predictive Analytics Tests**:
```python
# tests/test_forecasting_agent.py

import pytest
import pandas as pd
from consultantos.agents.forecasting_agent import ForecastingAgent
from consultantos.models.forecasting import ForecastMetric

@pytest.mark.asyncio
async def test_forecast_generation(mock_prophet_model):
    """Test forecast generation with Prophet."""

    agent = ForecastingAgent()
    agent.anomaly_detector = mock_prophet_model

    response = await agent.execute(
        company="Tesla",
        metrics=[ForecastMetric.REVENUE],
        horizon_months=6
    )

    assert "revenue" in response.forecasts
    assert len(response.forecasts["revenue"]["forecast_values"]) > 0

@pytest.mark.asyncio
async def test_scenario_simulation():
    """Test scenario simulation."""

    simulator = ScenarioSimulator()

    base_forecasts = {
        "revenue": {
            "forecast_values": [
                {"date": "2025-01-01", "predicted_value": 100, "lower_bound": 90, "upper_bound": 110}
            ]
        }
    }

    scenario = ScenarioParameters(
        name="price_cut",
        price_change_pct=-20
    )

    result = await simulator.simulate(
        base_forecasts=base_forecasts,
        parameters=scenario,
        horizon_months=6
    )

    # Revenue should decrease with price cut
    adjusted_value = result["adjusted_forecasts"]["revenue"]["forecast_values"][0]["predicted_value"]
    assert adjusted_value < 100
```

**Dark Data Mining Tests**:
```python
# tests/test_dark_data_agent.py

import pytest
from consultantos.agents.dark_data_agent import DarkDataAgent
from consultantos.utils.privacy_manager import PrivacyManager

@pytest.mark.asyncio
async def test_pii_redaction():
    """Test PII detection and redaction."""

    privacy_manager = PrivacyManager()

    document = {
        "body": "Contact me at john@example.com or 555-123-4567"
    }

    sanitized = await privacy_manager.redact_pii(document)

    assert "[EMAIL_REDACTED]" in sanitized["body"]
    assert "[PHONE_REDACTED]" in sanitized["body"]
    assert "john@example.com" not in sanitized["body"]

@pytest.mark.asyncio
async def test_entity_extraction(mock_nlp_processor):
    """Test entity extraction from documents."""

    processor = mock_nlp_processor

    documents = [
        {"body": "Tesla announced new partnership with BYD"}
    ]

    entities = await processor.extract_entities(documents)

    assert len(entities) >= 2
    assert any(e["entity_name"] == "Tesla" for e in entities)
    assert any(e["entity_name"] == "BYD" for e in entities)
```

### Integration Tests

**Conversational Flow Test**:
```python
# tests/integration/test_conversational_flow.py

@pytest.mark.asyncio
async def test_multi_turn_conversation(test_client):
    """Test multi-turn conversation with context preservation."""

    # Create conversation
    response = await test_client.post("/chat/conversations", json={
        "user_id": "test_user"
    })
    conv_id = response.json()["conversation_id"]

    # First query
    response = await test_client.post(
        f"/chat/conversations/{conv_id}/messages",
        json={"query": "What is Tesla's market position?", "stream": False}
    )
    assert response.status_code == 200

    # Follow-up query (testing context)
    response = await test_client.post(
        f"/chat/conversations/{conv_id}/messages",
        json={"query": "How does that compare to BYD?", "stream": False}
    )
    assert response.status_code == 200
    # Should understand "that" refers to Tesla from previous context
```

**Forecasting Pipeline Test**:
```python
# tests/integration/test_forecasting_pipeline.py

@pytest.mark.asyncio
async def test_forecast_to_visualization(test_client):
    """Test full forecasting pipeline."""

    # Generate forecast
    response = await test_client.post("/forecasting/generate", json={
        "company": "Tesla",
        "metrics": ["revenue", "market_share"],
        "horizon_months": 6
    })

    assert response.status_code == 200
    forecast_id = response.json()["forecast_id"]

    # Run scenario
    response = await test_client.post("/forecasting/scenarios", json={
        "forecast_id": forecast_id,
        "scenario": {
            "name": "price_cut",
            "price_change_pct": -10
        }
    })

    assert response.status_code == 200
    scenario_id = response.json()["scenario_id"]

    # Compare scenarios
    response = await test_client.post("/forecasting/compare", json={
        "forecast_id": forecast_id,
        "scenario_ids": [scenario_id],
        "metrics_to_compare": ["revenue"]
    })

    assert response.status_code == 200
```

### E2E Tests

**End-to-End Conversational AI**:
```python
# tests/e2e/test_conversational_e2e.py

@pytest.mark.e2e
async def test_conversational_intelligence_flow(browser, test_user):
    """Test full conversational flow from UI to response."""

    # Navigate to chat UI
    page = await browser.new_page()
    await page.goto("http://localhost:3000/dashboard/chat")

    # Log in
    await page.fill("#api-key-input", test_user.api_key)
    await page.click("#login-button")

    # Start conversation
    await page.fill("#query-input", "Compare Tesla vs BYD market share")
    await page.click("#send-button")

    # Wait for streaming response
    await page.wait_for_selector(".message.assistant", timeout=10000)

    # Verify response contains expected entities
    response_text = await page.text_content(".message.assistant")
    assert "Tesla" in response_text
    assert "BYD" in response_text
    assert "market" in response_text.lower()

    # Follow-up query
    await page.fill("#query-input", "What about their battery technology?")
    await page.click("#send-button")

    await page.wait_for_selector(".message.assistant:nth-child(4)", timeout=10000)

    # Verify context preserved (understands "their" = Tesla & BYD)
    response_text = await page.text_content(".message.assistant:nth-child(4)")
    assert "battery" in response_text.lower()
```

**End-to-End Dark Data Mining**:
```python
# tests/e2e/test_dark_data_e2e.py

@pytest.mark.e2e
async def test_dark_data_extraction_flow(browser, test_user):
    """Test dark data extraction from Gmail."""

    page = await browser.new_page()
    await page.goto("http://localhost:3000/dashboard/dark-data")

    # Connect Gmail
    await page.click("#connect-gmail-button")

    # Handle OAuth flow (mock for testing)
    await page.wait_for_selector("#oauth-success", timeout=30000)

    # Trigger extraction
    await page.click("#extract-button")

    # Wait for extraction job
    await page.wait_for_selector(".extraction-complete", timeout=60000)

    # Verify insights displayed
    insights = await page.query_selector_all(".insight-card")
    assert len(insights) > 0

    # Verify PII redacted
    insight_text = await insights[0].text_content()
    assert "[EMAIL_REDACTED]" not in insight_text or "@" not in insight_text
```

### Coverage Targets

- **Unit Tests**: ≥80% code coverage for all new agents and utilities
- **Integration Tests**: 100% coverage of agent orchestration flows
- **E2E Tests**: 100% coverage of critical user journeys

---

## Deployment & Migration

### Deployment Strategy

**Phase 1: Infrastructure Setup**
```bash
# 1. Create Firestore indexes
firebase firestore:indexes:deploy firestore.indexes.json

# 2. Set up secrets in Secret Manager
gcloud secrets create OAUTH_ENCRYPTION_KEY --data-file=- < encryption_key.txt
gcloud secrets create GMAIL_CLIENT_ID --data-file=- < gmail_client_id.txt
gcloud secrets create GMAIL_CLIENT_SECRET --data-file=- < gmail_client_secret.txt

# 3. Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding OAUTH_ENCRYPTION_KEY \
  --member=serviceAccount:consultantos@PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

**Phase 2: Code Deployment**
```bash
# Deploy backend with new skills
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --set-env-vars "TAVILY_API_KEY=${TAVILY_API_KEY}" \
  --set-secrets "OAUTH_ENCRYPTION_KEY=OAUTH_ENCRYPTION_KEY:latest" \
  --set-secrets "GMAIL_CLIENT_ID=GMAIL_CLIENT_ID:latest" \
  --set-secrets "GMAIL_CLIENT_SECRET=GMAIL_CLIENT_SECRET:latest"

# Deploy frontend with new UI
cd frontend
npm run build
gcloud app deploy  # or use Cloud Run for frontend
```

**Phase 3: Data Migration**
```bash
# Backfill RAG documents from existing reports
python scripts/backfill_rag_documents.py

# Extend monitor snapshots with forecast fields
python scripts/migrate_monitor_snapshots.py
```

### Rollback Strategy

**Canary Deployment**:
```bash
# Deploy new version to 10% of traffic
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-phase1=10,consultantos-current=90

# Monitor metrics for 1 hour
# If metrics are good, increase to 50%
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-phase1=50,consultantos-current=50

# If metrics are good, increase to 100%
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-phase1=100
```

**Rollback Procedure**:
```bash
# If issues detected, rollback to previous revision
gcloud run services update-traffic consultantos \
  --to-revisions=consultantos-current=100

# Database schema rollback (if needed)
# Note: Firestore schema changes are additive, so rollback is usually safe
# New fields are optional and backward compatible
```

### Monitoring & Observability

**Metrics to Track**:
```python
# Custom metrics for Cloud Monitoring

from google.cloud import monitoring_v3

metrics_to_track = {
    "conversational_ai": [
        "query_latency",
        "rag_retrieval_time",
        "agent_execution_time",
        "cache_hit_rate",
        "conversation_length",
        "tokens_used_per_query"
    ],
    "predictive_analytics": [
        "forecast_generation_time",
        "scenario_simulation_time",
        "model_training_duration",
        "forecast_accuracy_mae",
        "forecast_accuracy_mape"
    ],
    "dark_data_mining": [
        "extraction_time_per_100_docs",
        "entity_extraction_time",
        "pii_detection_time",
        "insight_generation_rate",
        "documents_processed_per_hour"
    ]
}
```

**Alerts**:
```yaml
# alerting_rules.yaml

# Conversational AI alerts
- name: ConversationalAILatencyHigh
  condition: query_latency_p95 > 5s
  duration: 5m
  severity: warning
  action: notify_oncall

- name: RAGCacheHitRateLow
  condition: cache_hit_rate < 0.4
  duration: 10m
  severity: warning
  action: investigate_cache

# Predictive Analytics alerts
- name: ForecastAccuracyDegraded
  condition: forecast_accuracy_mape > 15%
  duration: 1d
  severity: warning
  action: retrain_models

# Dark Data Mining alerts
- name: PIIDetectionFailed
  condition: pii_detection_time > 5s
  duration: 5m
  severity: critical
  action: stop_extraction

- name: ExtractionRateLow
  condition: documents_processed_per_hour < 5000
  duration: 15m
  severity: warning
  action: scale_up
```

### Feature Flags

**Gradual Rollout**:
```python
# consultantos/config.py

FEATURE_FLAGS = {
    "conversational_ai_enabled": os.getenv("FEATURE_CONVERSATIONAL_AI", "false").lower() == "true",
    "predictive_analytics_enabled": os.getenv("FEATURE_PREDICTIVE_ANALYTICS", "false").lower() == "true",
    "dark_data_mining_enabled": os.getenv("FEATURE_DARK_DATA_MINING", "false").lower() == "true",
    "rag_enabled": os.getenv("FEATURE_RAG", "false").lower() == "true",
    "streaming_enabled": os.getenv("FEATURE_STREAMING", "false").lower() == "true"
}

# Use in endpoints
@router.post("/chat/conversations")
async def create_conversation(...):
    if not FEATURE_FLAGS["conversational_ai_enabled"]:
        raise HTTPException(status_code=503, detail="Feature not available")

    # ... implementation
```

---

## Summary & Next Steps

### Implementation Roadmap

**Week 1-2: Foundation**
- [ ] Set up Firestore schema (8 new collections)
- [ ] Implement base agents (ConversationalAgent, ForecastingAgent, DarkDataAgent)
- [ ] Build data connectors (Gmail, Slack)
- [ ] Implement RAG system (embeddings + vector search)

**Week 3-4: Core Features**
- [ ] Build conversational flow (query parsing, routing, response generation)
- [ ] Implement forecasting pipeline (Prophet integration, scenario simulation)
- [ ] Build dark data processing (NLP, entity extraction, privacy controls)
- [ ] Add API endpoints for all three skills

**Week 5-6: Integration**
- [ ] Integrate with existing AnalysisOrchestrator
- [ ] Extend IntelligenceMonitor with dark data signals
- [ ] Build frontend UI components (chat, forecasting, dark data dashboard)
- [ ] Implement caching strategy

**Week 7-8: Testing & Optimization**
- [ ] Write unit tests (≥80% coverage)
- [ ] Write integration tests
- [ ] Write E2E tests
- [ ] Performance optimization (caching, parallel execution)
- [ ] Security audit (PII detection, RBAC, encryption)

**Week 9-10: Deployment**
- [ ] Deploy to Cloud Run (canary deployment)
- [ ] Data migration (backfill RAG documents)
- [ ] Monitoring setup (metrics, alerts, dashboards)
- [ ] Documentation (API docs, user guides)
- [ ] Launch beta to select users

### Success Metrics

**Conversational AI**:
- [ ] Response time <5s (p95)
- [ ] Cache hit rate >60%
- [ ] User satisfaction >4/5
- [ ] Conversation length >3 turns avg

**Predictive Analytics**:
- [ ] Forecast accuracy MAE <15% (3-month horizon)
- [ ] Forecast generation time <10s (p95)
- [ ] User adoption >50% of monitors

**Dark Data Mining**:
- [ ] Documents processed >10,000/hour
- [ ] PII detection accuracy >95%
- [ ] Insight generation rate >100/hour
- [ ] Zero PII leaks (GDPR compliance)

### Risk Mitigation

**Technical Risks**:
- LLM latency → Implement caching + streaming
- Forecast accuracy → Ensemble models + regular retraining
- PII leaks → Multi-layer privacy controls + auditing

**Operational Risks**:
- OAuth token expiration → Automatic token refresh
- API quota limits → Rate limiting + usage monitoring
- Data source changes → Graceful degradation + error handling

**Business Risks**:
- User adoption → Beta program + feedback loops
- Cost overruns → Usage tracking + budget alerts
- Privacy concerns → GDPR compliance + transparency

---

**End of Architecture Document**

