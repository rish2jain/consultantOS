# ConsultantOS Agents Documentation

## Overview

ConsultantOS uses a multi-agent architecture with specialized AI agents for different aspects of competitive intelligence analysis. The platform includes 5 core agents plus multiple advanced agents for specialized capabilities.

## Core Agents

### 1. ResearchAgent
- **Purpose**: Gather company intelligence using web search
- **Location**: `consultantos/agents/research_agent.py`
- **Tools**: Tavily API
- **Output**: `CompanyResearch` model with NLP enrichment
- **Features**: Entity extraction, sentiment analysis, keyword extraction

### 2. MarketAgent
- **Purpose**: Analyze market trends and consumer interest
- **Location**: `consultantos/agents/market_agent.py`
- **Tools**: Google Trends (pytrends)
- **Output**: `MarketTrends` model
- **Features**: Search interest trends, geographic distribution, competitor comparison

### 3. FinancialAgent
- **Purpose**: Extract financial metrics and analyst sentiment
- **Location**: `consultantos/agents/financial_agent.py`
- **Tools**: yfinance, Finnhub, Alpha Vantage
- **Output**: `FinancialSnapshot` model
- **Features**: Cross-source validation, analyst consensus, news sentiment

### 4. FrameworkAgent
- **Purpose**: Apply strategic business frameworks
- **Location**: `consultantos/agents/framework_agent.py`
- **Tools**: Google Gemini AI
- **Output**: `FrameworkAnalysis` model
- **Frameworks**: Porter's Five Forces, SWOT, PESTEL, Blue Ocean Strategy

### 5. SynthesisAgent
- **Purpose**: Create executive summary from all analysis
- **Location**: `consultantos/agents/synthesis_agent.py`
- **Tools**: Google Gemini AI
- **Output**: `ExecutiveSummary` model
- **Features**: Confidence scoring, prioritized recommendations, risk assessment

## Advanced Agents

### 6. ForecastingAgent
- **Purpose**: Multi-scenario financial forecasting using Monte Carlo simulation
- **Location**: `consultantos/agents/forecasting_agent.py`
- **Tools**: NumPy, SciPy for statistical analysis
- **Output**: `ForecastResult` model
- **Features**: Multiple scenarios, statistical validation, confidence intervals

### 7. WargamingAgent
- **Purpose**: Competitive scenario planning and simulation
- **Location**: `consultantos/agents/wargaming_agent.py`
- **Tools**: NumPy, SciPy for Monte Carlo simulation
- **Output**: `WargamingResult` model
- **Features**: Win probability calculations, risk assessment, statistical validation

### 8. SocialMediaAgent
- **Purpose**: Social media sentiment analysis and trend tracking
- **Location**: `consultantos/agents/social_media_agent.py`
- **Tools**: Reddit (PRAW), Twitter (Tweepy), Grok API (via laozhang.ai)
- **Output**: `SocialMediaInsights` model
- **Features**: Multi-platform sentiment, trend identification, influencer detection

### 9. DarkDataAgent
- **Purpose**: Extract insights from unstructured data sources
- **Location**: `consultantos/agents/dark_data_agent.py`
- **Tools**: NLP libraries (spaCy, TextBlob)
- **Output**: `DarkDataInsights` model
- **Features**: Email parsing, document extraction, entity extraction

### 10. ConversationalAgent
- **Purpose**: RAG-based conversational AI with intelligent query routing
- **Location**: `consultantos/agents/conversational_agent.py`
- **Tools**: ChromaDB for vector storage, RAG retrieval
- **Output**: `ConversationalResponse` model
- **Features**: RAG retrieval, query routing, conversation history, source citation

## Agent Architecture

All agents inherit from `BaseAgent` which provides:
- Gemini + Instructor setup for structured outputs
- Timeout handling (60s per agent)
- Error logging with context
- Performance tracking
- Sentry integration

## Project Structure & Module Organization
`consultantos/` contains the FastAPI backend: `agents/` holds all analyst agents, `orchestrator/` sequences their phases, and `tools/` wraps Tavily, Google Trends, SEC, and market-data clients. Shared routers sit in `api/`, schemas in `models/`, while `reports/` and `visualizations/` produce PDFs and dashboards. The Next.js dashboard lives in `frontend/` with primitives under `frontend/components` and static assets in `frontend/public`. Tests mirror this layout via `tests/` for Python modules and `frontend/__tests__/` for UI logic.

## Build, Test & Development Commands
```bash
pip install -r requirements.txt            # Sync backend deps
uvicorn consultantos.api.main:app --reload # Local API on :8080 (or set PORT env var for alternative ports)
pytest                                     # Backend suite & coverage
cd frontend && npm install && npm run dev  # Dashboard on :3000
npm run lint                               # Next.js lint/format gate
docker build -t consultantos .             # Cloud Run-ready image
```

## Coding Style & Naming Conventions
Target Python 3.11, 4-space indents, and concise docstrings. Agents end with `Agent`, async functions use snake_case, Pydantic models use UpperCamelCase, and constants stay UPPER_SNAKE_CASE. Every log entry should capture `report_id`, `company`, and `user_id`. Frontend code is TypeScript with ESLint + Prettier; stick to functional React components, Tailwind or CSS modules for styling, and colocate shared UI in `frontend/components`.

## Testing Guidelines
Use `pytest` with `pytest.mark.asyncio` for coroutine flows, stubbing network traffic at the tool boundary. Keep coverage ≥80%, emphasizing orchestrator transitions and the `/analyze` route. Tests should shadow source names (`tests/test_orchestrator.py`, `frontend/__tests__/dashboard.test.tsx`), and fixtures belong in `tests/fixtures` with descriptive names like `analysis_request.json`. Run `npm test` (Jest + Testing Library) for UI interactions; prefer event-driven assertions over brittle snapshots.

## Commit & Pull Request Guidelines
Craft imperative commit titles under ~65 characters (e.g., "Add Tavily retries"). Group related edits, explain the scenario plus verification steps in the body, and note any new env vars or migrations. PRs must link the motivating issue, list commands executed, attach screenshots for UI-visible changes, and document rollout considerations so Cloud Run deploys remain predictable.

## Security & Configuration Tips
Never hardcode `GEMINI_API_KEY`, `TAVILY_API_KEY`, or Google Cloud credentials—load them via `config.py` and local `.env` files (git-ignored). Cloud Run instances should source secrets from Secret Manager and treat cache storage as ephemeral. Sanitize user inputs before logging or persisting, and manually review generated PDFs or dashboards before sharing externally.
