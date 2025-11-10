# Conversational AI - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies
```bash
pip install sentence-transformers>=2.2.2
```

All other dependencies (chromadb, google-generativeai, etc.) are already in requirements.txt.

### 2. Start the Server
```bash
cd /Users/rish2jain/Documents/Hackathons/ConsultantOS
python main.py
```

Or with auto-reload:
```bash
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

### 3. Test Chat Endpoint

**Basic Chat**:
```bash
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is competitive intelligence?",
    "use_rag": false
  }'
```

**Chat with RAG** (after indexing reports):
```bash
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are Tesla'\''s competitive advantages?",
    "use_rag": true,
    "filter_company": "Tesla"
  }'
```

**Response**:
```json
{
  "response": "Tesla's competitive advantages include...",
  "conversation_id": "conv_20251109_abc123",
  "sources": [
    {
      "content": "Tesla has vertical integration...",
      "source": "report_tesla_2024",
      "company": "Tesla",
      "relevance_score": 0.92
    }
  ],
  "routed_to_agent": null,
  "timestamp": "2025-11-09T12:00:00"
}
```

### 4. Index Reports for RAG

```bash
curl -X POST "http://localhost:8080/conversational/index-report" \
  -d "report_id=report_tesla_2024_q3" \
  -d "content=Tesla's Q3 2024 results show strong growth in EV deliveries. Key competitive advantages include vertical integration in battery production, the extensive Supercharger network, and advanced autopilot technology. Market position remains dominant with 65% market share in the US EV market." \
  -d "company=Tesla" \
  -d "industry=Electric Vehicles" \
  -d "report_type=quarterly_analysis"
```

### 5. Get RAG Stats

```bash
curl "http://localhost:8080/conversational/rag-stats"
```

**Response**:
```json
{
  "total_documents": 1,
  "collection_name": "consultantos_reports",
  "embedding_model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384
}
```

### 6. Test Conversation History

**Multi-turn conversation**:
```bash
# First message
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are Tesla'\''s main competitors?",
    "conversation_id": "my_conv_123"
  }'

# Follow-up (uses context from previous)
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do they compare in market share?",
    "conversation_id": "my_conv_123"
  }'
```

**Get history**:
```bash
curl "http://localhost:8080/conversational/history/my_conv_123"
```

**Clear history**:
```bash
curl -X DELETE "http://localhost:8080/conversational/history/my_conv_123"
```

---

## Python Client Usage

```python
import httpx
import asyncio

async def chat_example():
    async with httpx.AsyncClient() as client:
        # Chat request
        response = await client.post(
            "http://localhost:8080/conversational/chat",
            json={
                "query": "What are Tesla's competitive advantages?",
                "conversation_id": "test_123",
                "use_rag": True,
                "filter_company": "Tesla"
            }
        )

        data = response.json()
        print(f"Response: {data['response']}")
        print(f"Sources: {len(data['sources'])}")
        print(f"Routed to: {data['routed_to_agent']}")

asyncio.run(chat_example())
```

---

## Direct Agent Usage (Python)

```python
from consultantos.agents.conversational_agent import ConversationalAgent

async def agent_example():
    agent = ConversationalAgent(timeout=60)

    # Chat with RAG
    result = await agent.execute({
        "query": "What are Tesla's competitive advantages?",
        "conversation_id": "conv_test",
        "use_rag": True,
        "filter_company": "Tesla"
    })

    if result["success"]:
        response_data = result["data"]
        print(response_data["response"])
        print(f"Sources: {len(response_data['sources'])}")
    else:
        print(f"Error: {result['error']}")

# Run
import asyncio
asyncio.run(agent_example())
```

---

## Query Routing Examples

**Financial Query** (routes to FinancialAgent):
```bash
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are Tesla'\''s latest earnings and revenue?"}'
```

**Market Trends Query** (routes to MarketAgent):
```bash
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the current market trends in electric vehicles?"}'
```

**Forecasting Query** (routes to ForecastingAgent):
```bash
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Predict Tesla'\''s revenue for next quarter"}'
```

**General Query** (uses RAG, no routing):
```bash
curl -X POST "http://localhost:8080/conversational/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about competitive intelligence strategies"}'
```

---

## Indexing Historical Reports (Batch)

```python
from consultantos.agents.conversational_agent import ConversationalAgent
import asyncio

async def index_reports():
    agent = ConversationalAgent()

    reports = [
        {
            "content": "Tesla Q3 2024: Strong growth, 65% US market share...",
            "metadata": {
                "source": "report_tesla_2024_q3",
                "company": "Tesla",
                "industry": "Electric Vehicles",
                "report_type": "quarterly_analysis"
            }
        },
        {
            "content": "Rivian Q3 2024: Growing production capacity...",
            "metadata": {
                "source": "report_rivian_2024_q3",
                "company": "Rivian",
                "industry": "Electric Vehicles",
                "report_type": "quarterly_analysis"
            }
        }
    ]

    # Batch index
    contents = [r["content"] for r in reports]
    metadatas = [r["metadata"] for r in reports]

    doc_ids = await agent.retriever.index_documents_batch(
        contents=contents,
        metadatas=metadatas
    )

    print(f"Indexed {len(doc_ids)} reports")
    print(f"Document IDs: {doc_ids}")

asyncio.run(index_reports())
```

---

## Testing

### Run All Conversational Tests
```bash
pytest tests/test_conversational*.py tests/test_rag_system.py tests/test_query_routing.py -v
```

### Run Specific Test File
```bash
pytest tests/test_conversational_agent.py -v
pytest tests/test_rag_system.py -v
pytest tests/test_query_routing.py -v
pytest tests/test_conversational_endpoints.py -v
```

### Run with Coverage
```bash
pytest tests/test_conversational*.py tests/test_rag_system.py tests/test_query_routing.py \
  --cov=consultantos.rag \
  --cov=consultantos.routing \
  --cov=consultantos.agents.conversational_agent \
  --cov=consultantos.api.conversational_endpoints \
  --cov-report=html \
  -v
```

---

## API Documentation

Once server is running:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

Filter by tag: **"conversational"**

---

## Troubleshooting

### Issue: Embedding model download slow
**Solution**: First run downloads ~90MB model. Subsequent runs are instant.
```python
# Pre-download model
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
```

### Issue: ChromaDB persistence errors
**Solution**: Check permissions on persist_directory
```bash
mkdir -p ./data/chromadb
chmod 755 ./data/chromadb
```

### Issue: Firestore not available (development)
**Solution**: Agent works without Firestore - conversation history just won't persist
```python
# Conversation history only in-memory without Firestore
agent = ConversationalAgent()  # Works fine, history not persisted
```

### Issue: RAG returns no results
**Solution**: Index some reports first
```bash
curl -X POST "http://localhost:8080/conversational/index-report" \
  -d "report_id=test_report" \
  -d "content=Test content about Tesla..." \
  -d "company=Tesla"
```

---

## Next Steps

1. **Index Historical Reports**: Use `/conversational/index-report` to build knowledge base
2. **Test Query Routing**: Try queries that trigger different agents
3. **Explore Conversation History**: Create multi-turn conversations
4. **Integrate with Frontend**: Connect dashboard to chat endpoint
5. **Monitor RAG Stats**: Track indexed documents with `/rag-stats`

---

**Ready to use!** 🚀

For full documentation, see: `claudedocs/CONVERSATIONAL_AI_IMPLEMENTATION.md`
