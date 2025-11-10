# Phase 1 Skills - Quick Start Guide

**For Developers**: Get started implementing Phase 1 skills in 30 minutes

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account with Firestore enabled
- Gemini API key
- Tavily API key

---

## 30-Minute Quick Start

### Step 1: Set Up Database (5 minutes)

```bash
# Create firestore.indexes.json
cat > firestore.indexes.json << 'EOF'
{
  "indexes": [
    {
      "collectionGroup": "conversations",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "user_id", "order": "ASCENDING"},
        {"fieldPath": "created_at", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "conversation_messages",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "conversation_id", "order": "ASCENDING"},
        {"fieldPath": "timestamp", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "rag_documents",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "report_id", "order": "ASCENDING"},
        {"fieldPath": "chunk_index", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "forecasts",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "monitor_id", "order": "ASCENDING"},
        {"fieldPath": "generated_at", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "dark_data_insights",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "source_id", "order": "ASCENDING"},
        {"fieldPath": "created_at", "order": "DESCENDING"}
      ]
    }
  ]
}
EOF

# Deploy indexes
firebase firestore:indexes:deploy
```

### Step 2: Install Dependencies (3 minutes)

```bash
# Add to requirements.txt
cat >> requirements.txt << 'EOF'

# Phase 1 dependencies
slack-sdk==3.23.0  # Slack connector
google-api-python-client==2.108.0  # Gmail connector
prophet==1.1.5  # Forecasting (already in requirements)
scikit-learn==1.3.2  # For cosine similarity in RAG
EOF

# Install
pip install -r requirements.txt
```

### Step 3: Create Minimal Conversational Agent (10 minutes)

```bash
# Create consultantos/agents/conversational_agent.py
mkdir -p consultantos/agents
cat > consultantos/agents/conversational_agent.py << 'AGENT_EOF'
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.conversational import ConversationResponse
import instructor
from pydantic import BaseModel

class ConversationalAgent(BaseAgent):
    """Minimal conversational agent for MVP."""

    def __init__(self):
        super().__init__(agent_name="conversational")

    async def _execute_internal(self, query: str, **kwargs) -> ConversationResponse:
        """Execute conversational query."""

        # Simple pass-through to Gemini for MVP
        prompt = f"""You are an AI competitive intelligence analyst. Answer this query:

{query}

Provide a concise, professional response."""

        response = await self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        response_text = response.choices[0].message.content

        return ConversationResponse(
            response_text=response_text,
            agents_used=["conversational"],
            rag_documents_used=0,
            suggested_followups=[],
            response_time=0.0,
            tokens_used=response.usage.total_tokens
        )
AGENT_EOF

# Create models
cat > consultantos/models/conversational.py << 'MODEL_EOF'
from pydantic import BaseModel
from typing import List, Optional

class ConversationResponse(BaseModel):
    """Conversational AI response."""
    response_text: str
    agents_used: List[str] = []
    rag_documents_used: int = 0
    suggested_followups: List[str] = []
    response_time: float
    tokens_used: int
MODEL_EOF
```

### Step 4: Create Minimal API Endpoint (5 minutes)

```bash
# Create consultantos/api/chat_endpoints.py
cat > consultantos/api/chat_endpoints.py << 'API_EOF'
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from consultantos.agents.conversational_agent import ConversationalAgent
import time

router = APIRouter(prefix="/chat", tags=["conversational-ai"])

class ChatRequest(BaseModel):
    query: str

@router.post("/query")
async def chat_query(request: ChatRequest):
    """Simple chat query endpoint."""

    agent = ConversationalAgent()

    start_time = time.time()
    response = await agent.execute(query=request.query)
    response.response_time = time.time() - start_time

    return response
API_EOF

# Add router to main.py
cat >> consultantos/api/main.py << 'MAIN_EOF'

# Phase 1: Conversational AI
from consultantos.api.chat_endpoints import router as chat_router
app.include_router(chat_router)
MAIN_EOF
```

### Step 5: Test Conversational AI (3 minutes)

```bash
# Start server
python main.py &

# Wait for startup
sleep 5

# Test query
curl -X POST "http://localhost:8080/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Tesla'\''s competitive advantage?"}'

# Expected output:
# {
#   "response_text": "Tesla's competitive advantages include...",
#   "agents_used": ["conversational"],
#   "rag_documents_used": 0,
#   "suggested_followups": [],
#   "response_time": 2.5,
#   "tokens_used": 450
# }
```

### Step 6: Create Minimal Forecasting Agent (4 minutes)

```bash
# Create consultantos/agents/forecasting_agent.py
cat > consultantos/agents/forecasting_agent.py << 'FORECAST_EOF'
from consultantos.agents.base_agent import BaseAgent
from consultantos.models.forecasting import ForecastResponse
from consultantos.monitoring.anomaly_detector import AnomalyDetector
import pandas as pd
from datetime import datetime, timedelta

class ForecastingAgent(BaseAgent):
    """Minimal forecasting agent for MVP."""

    def __init__(self):
        super().__init__(agent_name="forecasting")
        self.anomaly_detector = AnomalyDetector()

    async def _execute_internal(self, company: str, horizon_months: int = 6, **kwargs) -> ForecastResponse:
        """Generate simple forecast."""

        # For MVP: generate dummy forecast
        # In production, use real Prophet models from AnomalyDetector

        forecast_values = []
        current_date = datetime.utcnow()

        for i in range(horizon_months * 30):  # Daily forecasts
            date = current_date + timedelta(days=i)
            forecast_values.append({
                "date": date.isoformat(),
                "predicted_value": 100 + i * 0.5,  # Dummy trend
                "lower_bound": 90 + i * 0.5,
                "upper_bound": 110 + i * 0.5,
                "confidence_interval": 0.95
            })

        return ForecastResponse(
            company=company,
            monitor_id=None,
            forecasts={
                "revenue": {
                    "metric": "revenue",
                    "forecast_values": forecast_values,
                    "model_type": "dummy",
                    "training_samples": 365
                }
            },
            scenarios={},
            accuracy_metrics={},
            horizon_months=horizon_months,
            generated_at=datetime.utcnow()
        )
FORECAST_EOF

# Create models
cat > consultantos/models/forecasting.py << 'FMODEL_EOF'
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime

class ForecastResponse(BaseModel):
    """Forecast generation response."""
    company: str
    monitor_id: str | None
    forecasts: Dict[str, Any]
    scenarios: Dict[str, Any] = {}
    accuracy_metrics: Dict[str, float] = {}
    horizon_months: int
    generated_at: datetime
FMODEL_EOF

# Create API endpoint
cat > consultantos/api/forecasting_endpoints.py << 'FAPI_EOF'
from fastapi import APIRouter
from pydantic import BaseModel
from consultantos.agents.forecasting_agent import ForecastingAgent

router = APIRouter(prefix="/forecasting", tags=["predictive-analytics"])

class ForecastRequest(BaseModel):
    company: str
    horizon_months: int = 6

@router.post("/generate")
async def generate_forecast(request: ForecastRequest):
    """Generate forecast."""

    agent = ForecastingAgent()
    response = await agent.execute(
        company=request.company,
        horizon_months=request.horizon_months
    )

    return response
FAPI_EOF

# Add router
cat >> consultantos/api/main.py << 'FMAIN_EOF'

# Phase 1: Predictive Analytics
from consultantos.api.forecasting_endpoints import router as forecasting_router
app.include_router(forecasting_router)
FMAIN_EOF
```

---

## Test All Three Skills

```bash
# Test Conversational AI
curl -X POST "http://localhost:8080/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Compare Tesla vs BYD"}'

# Test Forecasting
curl -X POST "http://localhost:8080/forecasting/generate" \
  -H "Content-Type: application/json" \
  -d '{"company": "Tesla", "horizon_months": 6}'

# Check API docs
open http://localhost:8080/docs
```

---

## Next Steps

### Enhance Conversational AI

1. **Add RAG System**:
   - Implement `consultantos/utils/rag_system.py`
   - Index existing reports with embeddings
   - Retrieve relevant context before generating response

2. **Add Query Router**:
   - Implement `consultantos/utils/query_router.py`
   - Route queries to appropriate agents (Research, Market, Financial)
   - Combine results before responding

3. **Add Conversation State**:
   - Implement `consultantos/utils/conversation_state.py`
   - Store conversation history in Firestore
   - Maintain context across turns

### Enhance Forecasting

1. **Integrate Real Prophet Models**:
   - Extend `AnomalyDetector` with `forecast()` method
   - Use actual historical data from `TimeSeriesOptimizer`
   - Train Prophet models weekly

2. **Add Scenario Simulation**:
   - Implement `consultantos/utils/scenario_simulator.py`
   - Allow "what-if" parameter adjustments
   - Run Monte Carlo simulations

3. **Add Accuracy Tracking**:
   - Store forecasts in Firestore
   - Compare with actual values
   - Calculate MAE, RMSE, MAPE

### Implement Dark Data Mining

1. **Create Data Connectors**:
   - Implement `consultantos/utils/data_connectors.py`
   - Add OAuth2 flow for Gmail, Slack
   - Extract documents incrementally

2. **Create NLP Pipeline**:
   - Implement `consultantos/utils/dark_data_processor.py`
   - Reuse existing `NLPProcessor`
   - Extract entities, relationships, sentiment

3. **Add Privacy Controls**:
   - Implement `consultantos/utils/privacy_manager.py`
   - PII detection and redaction
   - GDPR compliance (right-to-delete)

---

## Debugging Tips

### Conversational AI Not Responding

```bash
# Check logs
tail -f logs/consultantos.log | grep "conversational"

# Test agent directly
python -c "
import asyncio
from consultantos.agents.conversational_agent import ConversationalAgent

async def test():
    agent = ConversationalAgent()
    response = await agent.execute(query='Test query')
    print(response)

asyncio.run(test())
"
```

### Forecasting Errors

```bash
# Check Prophet installation
python -c "import prophet; print(prophet.__version__)"

# Test AnomalyDetector
python -c "
from consultantos.monitoring.anomaly_detector import AnomalyDetector
detector = AnomalyDetector()
print('AnomalyDetector OK')
"
```

### Database Connection Issues

```bash
# Check Firestore credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test Firestore connection
python -c "
from consultantos.database import get_database
db = get_database()
print('Firestore OK')
"
```

---

## Performance Optimization

### Enable Caching

```python
# Add to consultantos/agents/conversational_agent.py

from consultantos.cache import cache

class ConversationalAgent(BaseAgent):

    @cache.memoize(ttl=3600)  # Cache for 1 hour
    async def _execute_internal(self, query: str, **kwargs):
        # ... existing code
```

### Enable Parallel Agent Execution

```python
# Modify query routing to run agents in parallel

import asyncio

async def _route_query(self, parsed_query, context):
    """Route query to agents in parallel."""

    tasks = []

    if "research" in agents_to_call:
        tasks.append(self.orchestrator.research_agent.execute(...))

    if "market" in agents_to_call:
        tasks.append(self.orchestrator.market_agent.execute(...))

    if "financial" in agents_to_call:
        tasks.append(self.orchestrator.financial_agent.execute(...))

    # Run in parallel
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return dict(zip(agents_to_call, results))
```

---

## Common Pitfalls

❌ **Don't**: Block event loop with sync I/O
```python
# BAD
def get_data():
    with open('file.txt') as f:
        return f.read()
```

✅ **Do**: Use async I/O
```python
# GOOD
async def get_data():
    async with aiofiles.open('file.txt') as f:
        return await f.read()
```

❌ **Don't**: Store secrets in code
```python
# BAD
GMAIL_CLIENT_SECRET = "abc123"
```

✅ **Do**: Use environment variables
```python
# GOOD
GMAIL_CLIENT_SECRET = os.getenv("GMAIL_CLIENT_SECRET")
```

❌ **Don't**: Trust user input
```python
# BAD
query = f"SELECT * FROM users WHERE name = '{user_input}'"
```

✅ **Do**: Sanitize and validate
```python
# GOOD
query = db.collection("users").where("name", "==", sanitize(user_input))
```

---

## Resources

- **Full Architecture**: `PHASE1_ARCHITECTURE.md` (3,565 lines)
- **Implementation Summary**: `PHASE1_IMPLEMENTATION_SUMMARY.md`
- **API Documentation**: http://localhost:8080/docs
- **Testing Guide**: `tests/README.md`

---

## Getting Help

**Common Issues**:
1. Import errors → Check `requirements.txt` installed
2. Firestore errors → Check `GOOGLE_APPLICATION_CREDENTIALS`
3. LLM errors → Check `GEMINI_API_KEY` set
4. Slow responses → Enable caching, use parallel execution

**Contact**:
- GitHub Issues: https://github.com/yourorg/consultantos/issues
- Slack: #consultantos-dev
- Email: dev@consultantos.com

---

**Estimated Time to Full Implementation**: 10 weeks (2 developers)
- Week 1-2: Foundation (database, agents, utilities)
- Week 3-4: Core features (API endpoints, models, integration)
- Week 5-6: Frontend (UI components, API integration)
- Week 7-8: Testing & security (unit, integration, E2E, security audit)
- Week 9-10: Deployment & launch (infrastructure, migration, beta rollout)
