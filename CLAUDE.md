# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ConsultantOS is a Comprehensive Competitive Intelligence Platform**

The platform orchestrates multiple specialized AI agents to provide comprehensive business intelligence. It has evolved from a simple report generator to a full-featured intelligence platform with advanced analytics, conversational AI, and strategic planning capabilities.

**Key Capabilities**:
- **Core Analysis**: 5 specialized agents (Research, Market, Financial, Framework, Synthesis)
- **Advanced Analytics**: Forecasting, Wargaming, Social Media Analysis, Dark Data Extraction
- **Conversational AI**: RAG-based chat with intelligent query routing
- **Strategic Intelligence**: Comprehensive competitive intelligence dashboards
- **Report Generation**: PDF, Excel, Word exports with interactive visualizations

**Tech Stack**: Python 3.11+, FastAPI, Google Gemini AI, Next.js 14 (frontend), Google Cloud Platform (Cloud Run, Firestore, Cloud Storage), Celery + Redis, Prometheus, Sentry

## Essential Commands

### Backend Development

**Start Server** (with auto-reload):
```bash
python main.py
# or
uvicorn consultantos.api.main:app --host 0.0.0.0 --port 8080 --reload
```

**Run Tests**:
```bash
pytest tests/ -v                    # Run all tests with verbose output
pytest tests/ --cov=consultantos   # Run with coverage report
pytest tests/test_agents.py -v     # Run specific test file
```

**Install Dependencies**:
```bash
pip install -r requirements.txt
```

**Environment Setup**:
Required environment variables in `.env`:
- `TAVILY_API_KEY` - Web research
- `GEMINI_API_KEY` - AI analysis

Optional:
- `GCP_PROJECT_ID` - For Firestore/Cloud Storage
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account JSON path
- `LOG_LEVEL` - Default: INFO
- `RATE_LIMIT_PER_HOUR` - Default: 10

### Frontend Development

```bash
cd frontend
npm install           # Install dependencies
npm run dev          # Start dev server (port 3000)
npm run build        # Production build
npm run lint         # Run ESLint
```

### Deployment

**Deploy to Cloud Run**:
```bash
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"
```

## Architecture

### Advanced Analytics System

**Multi-Scenario Forecasting**:
- Monte Carlo simulation for financial projections
- Multiple scenarios (optimistic, base, pessimistic)
- Statistical validation with confidence intervals

**Wargaming Simulator**:
- Competitive scenario planning
- Monte Carlo simulation with statistical validation
- Risk assessment and win probability calculations

**Social Media Analysis**:
- Reddit and Twitter sentiment tracking
- Trend analysis and influencer identification
- Real-time sentiment monitoring

**Dark Data Extraction**:
- Unstructured data analysis
- Email and document parsing
- Hidden insights discovery

**Conversational AI**:
- RAG-based retrieval from historical reports
- Intelligent query routing to specialized agents
- Conversation history management
- Source citation and transparency

### Multi-Agent Orchestration (Used by Monitoring System)

The system uses a **phased execution model** coordinated by `AnalysisOrchestrator`:

1. **Phase 1 (Parallel)**: Research, Market, and Financial agents run concurrently
2. **Phase 2 (Sequential)**: Framework agent applies business frameworks (Porter's 5 Forces, SWOT, PESTEL, Blue Ocean Strategy)
3. **Phase 3**: Synthesis agent creates executive summary
4. **Optional**: PDF Generation (ReportLab + Plotly) - now secondary export option

**Graceful Degradation**: Partial results returned with adjusted confidence if agents fail

### Project Structure

```
consultantos/
├── agents/          # Specialized agents inheriting from BaseAgent
│   ├── research_agent.py         # Web research via Tavily
│   ├── market_agent.py           # Trends via pytrends
│   ├── financial_agent.py       # Financial data (yfinance, SEC EDGAR)
│   ├── framework_agent.py        # Strategic framework analysis
│   ├── synthesis_agent.py       # Executive summary generation
│   ├── forecasting_agent.py     # Multi-scenario forecasting
│   ├── wargaming_agent.py       # Competitive scenario simulation
│   ├── social_media_agent.py    # Social media sentiment analysis
│   ├── dark_data_agent.py       # Unstructured data extraction
│   ├── conversational_agent.py # RAG-based conversational AI
│   └── [many more specialized agents]
├── orchestrator/    # Multi-agent coordination with caching
├── monitoring/      # Continuous intelligence monitoring system
│   ├── intelligence_monitor.py  # Core monitoring, change detection, alerts
│   └── __init__.py
├── api/             # FastAPI endpoints (thin layer - validation, auth, delegation)
│   ├── main.py                    # Main app, CORS, rate limiting, routes
│   ├── integration_endpoints.py  # Comprehensive analysis integration
│   ├── forecasting_endpoints.py  # Forecasting endpoints
│   ├── wargaming_endpoints.py    # Wargaming endpoints
│   ├── conversational_endpoints.py # Conversational AI endpoints
│   ├── social_media_endpoints.py # Social media endpoints
│   ├── strategic_intelligence_endpoints.py # Strategic intelligence
│   ├── monitoring_endpoints.py   # Monitor CRUD, alerts, feedback
│   ├── user_endpoints.py
│   ├── template_endpoints.py
│   ├── sharing_endpoints.py
│   ├── versioning_endpoints.py
│   ├── comments_endpoints.py
│   ├── community_endpoints.py
│   ├── analytics_endpoints.py
│   └── [many more endpoint modules]
├── models/          # Pydantic domain models (shared across app)
│   ├── monitoring.py             # Monitor, Alert, Change models
│   ├── forecasting.py            # Forecasting models
│   ├── wargaming.py              # Wargaming models
│   ├── conversational.py         # Conversational AI models
│   └── [many more model files]
├── tools/           # External data integrations
│   ├── tavily_tool.py           # Tavily search
│   ├── trends_tool.py           # Google Trends
│   ├── financial_tool.py        # yfinance, SEC EDGAR
│   └── [more tool integrations]
├── connectors/      # External service connectors
│   ├── reddit_connector.py      # Reddit API
│   ├── twitter_connector.py     # Twitter API
│   └── grok_connector.py        # Grok API via laozhang.ai
├── reports/         # PDF generation and exports (JSON, Excel, Word)
├── visualizations/  # Plotly chart generation
├── jobs/            # Async job queue and worker
│   ├── queue.py
│   ├── worker.py
│   └── monitoring_worker.py      # Background monitoring scheduler
├── services/        # Cross-cutting services (email, notifications)
├── utils/           # Validation, sanitization, retry, circuit breaker
├── cache.py         # Multi-level caching (disk + semantic)
├── storage.py       # Cloud Storage integration
├── database.py      # Firestore database layer
├── auth.py          # API key authentication
├── log_utils.py     # Structured logging (renamed from monitoring.py)
├── observability/   # Observability and monitoring
│   ├── metrics.py               # Prometheus metrics
│   └── sentry_integration.py    # Sentry error tracking
└── config.py          # Configuration management (pydantic-settings)

frontend/
├── app/             # Next.js 14 app directory
│   └── dashboard/           # **NEW**: Real-time monitoring dashboard
│       └── page.tsx
├── components/      # React components
└── public/          # Static assets
```

### Key Architectural Patterns

**BaseAgent Pattern**: All agents inherit from `BaseAgent` which provides:
- Gemini + Instructor setup for structured outputs
- Timeout handling
- Error logging with context

**Caching Strategy**:
- Disk cache (diskcache) for persistence
- Semantic cache for deduping similar analyses
- Multi-level lookup in orchestrator

**Async Processing**:
- `/analyze` - Synchronous (quick analyses, waits for completion)
- `/analyze/async` - Asynchronous (enqueues job, returns job_id)
- `/integration/comprehensive-analysis` - Full-featured analysis with all capabilities
- Use async for >3 frameworks or deep analysis depth
- Celery + Redis for distributed task processing

**Error Handling**:
- Convert internal exceptions to HTTPException at API boundary
- Return partial_success when PDF fails but analysis completes
- Graceful degradation: adjust confidence when agents fail
- Never leak secrets in error messages

**Authentication**:
- Optional API key via `X-API-Key` header or `?api_key=` query param
- Required for user-specific features (history, sharing, templates)
- Public endpoints work without authentication

## Development Guidelines

### Code Style

**Python Conventions**:
- Python 3.11+ with type hints
- Modules: `snake_case`, Classes: `PascalCase`, functions/vars: `snake_case`
- Agents named with `Agent` suffix
- Constants: `UPPER_SNAKE_CASE`

**Async Patterns**:
- Agents implement async `execute()` with per-agent timeouts
- Orchestrator uses `asyncio.gather()` with graceful degradation
- Never block event loop with sync I/O in async endpoints
- Offload long tasks to background jobs

**Validation & Sanitization**:
- Validate all inputs at API boundary using `AnalysisRequestValidator`
- Sanitize strings with `utils.validators` before processing/logging
- Never trust user input

### Testing Strategy

**Structure**: `tests/` mirrors `consultantos/` modules

**Test Types**:
- **Unit**: Agent internals, validators, tools, cache keying (≥80% coverage)
- **Integration**: Orchestrator phases, `/analyze` endpoint with mocked services
- **Contract**: Pydantic model validation, API response schemas

**Mocking**:
- Mock all external APIs (Tavily, pytrends, yfinance, edgartools) using `monkeypatch` or fixtures
- Use `FastAPI TestClient` for API tests
- Override dependencies: `get_storage_service`, `get_db_service`

**Running Tests**:
```bash
pytest tests/ -v                              # All tests
pytest tests/test_agents.py::test_research -v # Specific test
pytest tests/ --cov=consultantos --cov-report=html
```

**Async Tests**:
- Use `pytest-asyncio` with `asyncio_mode = auto` (configured in `pytest.ini`)
- Mark async tests with `@pytest.mark.asyncio` if needed

### Common Tasks

**Add a New Agent**:
1. Create in `consultantos/agents/` inheriting from `BaseAgent`
2. Implement `async _execute_internal()` returning Pydantic model
3. Add to orchestrator phase execution
4. Add tests in `tests/test_agents.py` with mocked dependencies

**Add API Endpoint**:
1. Define route in appropriate `consultantos/api/*_endpoints.py`
2. Import and include router in `consultantos/api/main.py`
3. Add Pydantic request/response models in `consultantos/models/`
4. Validate inputs, delegate to agents/orchestrator
5. Add tests using `TestClient`

**Modify Business Frameworks**:
- Framework logic lives in `FrameworkAgent._execute_internal()`
- Framework prompts in `consultantos/prompts.py`
- Use structured outputs via Instructor + Pydantic models

**Update PDF Generation**:
- Main logic in `consultantos/reports/pdf_generator.py`
- Charts via `consultantos/visualizations/` (Plotly + kaleido)
- Gracefully handle rendering failures (return partial_success)

### Important Notes

**Dependency Boundaries**:
- Keep business logic in agents, orchestrator, and tools
- API layer should be thin (validation, auth, delegation only)
- Reports module is presentation-only (no business logic)

**External Services**:
- Firestore and Cloud Storage are optional for development (in-memory fallback)
- Some packages (edgartools) have complex deps - marked optional
- Use `--no-deps` flag if httpx installation issues occur

**Rate Limiting**:
- Configured via slowapi at API layer
- Default: 10 requests/hour per IP
- Adjust via `RATE_LIMIT_PER_HOUR` env var

**Logging**:
- Use `monitoring.py` for structured logging
- Include context: `report_id`, `company`, `user_id`
- Never log secrets or API keys

**LLM Prompts**:
- Store in `consultantos/prompts.py`
- Include few-shot examples where helpful
- Response models via Pydantic in `consultantos/models/`

**Frontend Integration**:
- Backend: `http://localhost:8080`
- Frontend: `http://localhost:3000`
- Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Use signed URLs for report downloads (never expose storage paths)

## Quick Reference

**Health Check**: `curl http://localhost:8080/health`

**API Docs**:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc`

**Test Analysis**:
```bash
curl -X POST "http://localhost:8080/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "company": "Tesla",
    "industry": "Electric Vehicles",
    "frameworks": ["porter", "swot"]
  }'
```

**Check Logs**: Structured logs via `monitoring.py` - check stdout or Cloud Logging in production
