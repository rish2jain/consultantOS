### 📘 Project Best Practices

#### 1. Project Purpose
ConsultantOS is a Business Intelligence Research Engine that generates strategic analysis reports using a multi-agent system. It orchestrates research, market trends, financial data, and strategic frameworks (e.g., Porter's Five Forces, SWOT) to produce executive-ready PDFs. The project exposes a FastAPI backend, with optional Next.js frontend, and integrates Google Gemini, Tavily, pytrends, yfinance, and SEC Edgar for data. It targets independent consultants and strategy teams.

#### 2. Project Structure
- Root
  - consultantos/ — Python backend package with clear domain-driven folders
    - agents/ — Specialized agents (research, market, financial, framework, synthesis) built atop BaseAgent
    - api/ — FastAPI endpoints grouped by domain (users, templates, sharing, comments, community, analytics)
    - jobs/ — Async queue and worker for background processing
    - models/ — Pydantic domain models (requests, reports, comments, templates, etc.)
    - orchestrator/ — AnalysisOrchestrator coordinating multi-agent workflow and caching
    - reports/ — Exporters and PDF generation (ReportLab + Plotly image rendering)
    - services/ — Cross-cutting services (e.g., email)
    - tools/ — External data tools (tavily, trends, financial, ticker resolver)
    - utils/ — Validation, sanitization, retry, circuit-breaker helpers
    - visualizations/ — Plotly chart constructors used in reports
    - auth.py — API key verification, creation, rotation and validation
    - cache.py — Disk + semantic cache helpers
    - config.py — Settings management (pydantic-settings + env)
    - database.py — Persistence (Firestore metadata)
    - monitoring.py — Structured logging, metrics, tracing hooks
    - storage.py — Cloud Storage interface (PDF upload, signed URLs)
    - user_management.py — User-level operations
  - frontend/ — Next.js app (app router) with Tailwind CSS for UI
  - docs/ — Product and implementation docs (archive maintained under docs/archive)
  - tests/ — Pytest suite for agents, tools, models, utils, and API
  - cloudbuild.yaml / Dockerfile — CI/CD and containerization
  - requirements.txt / pytest.ini — Dependencies and test config

Guidelines:
- Keep business logic in agents, orchestration, and tools — keep API thin (validation, auth, delegation).
- Use reports/ only for presentation/export concerns; avoid business logic there.
- Place shared domain models in consultantos/models and import from there across the app.

#### 3. Test Strategy
- Frameworks: pytest, pytest-asyncio, pytest-cov.
- Structure: tests/ mirrors consultantos/ modules (e.g., test_agents.py, test_tools.py, test_api.py).
- Async: mark async tests with pytest-asyncio; prefer await over running loops manually.
- Mocking:
  - Mock network-bound tools (Tavily, pytrends, yfinance, edgartools) using monkeypatch or fixtures.
  - Use dependency seams: tools/* classes/functions and agent.execute calls should be isolated and mocked in unit tests.
  - For API tests, use FastAPI TestClient and override dependencies (e.g., get_storage_service, get_db_service).
- Types of tests:
  - Unit: agents._execute_internal, validators, tools utilities, cache keying.
  - Integration: orchestrator phases, API /analyze happy-path with mocked services, PDF generation pipeline with Plotly image rendering stubbed.
  - Contract: schema validation for Pydantic models; ensure API responses match documented fields.
- Coverage: target ≥80% lines; enforce critical paths (orchestrator, validators, api/analyze, pdf generation).

#### 4. Code Style
- Python 3.11+ with typing and pydantic models.
- Naming:
  - Modules: snake_case; Classes: PascalCase; functions/vars: snake_case; constants: UPPER_SNAKE_CASE.
  - Agents named with Agent suffix (ResearchAgent, MarketAgent, etc.).
- Async patterns:
  - Agents implement async execute with per-agent timeouts; orchestrator uses asyncio.gather with graceful degradation.
  - Avoid blocking I/O in async endpoints; offload long tasks to background jobs where appropriate.
- Docstrings and comments:
  - Public methods and endpoints require concise docstrings with examples where helpful.
  - Prefer structured logging fields over excessive inline comments.
- Error handling:
  - Convert internal exceptions to HTTPException in API boundary with appropriate status codes.
  - Log with context (report_id, company, user_id) and avoid leaking secrets.
  - Use graceful degradation: partial results and confidence adjustment when agents fail.
- Validation and sanitization:
  - Validate with utils.validators; sanitize string inputs to remove dangerous characters before processing or logging.

#### 5. Common Patterns
- BaseAgent: shared setup for Gemini + Instructor; subclass-specific _execute_internal implementations return structured outputs.
- Orchestrator: phased execution (parallel data, framework analysis, synthesis) with semantic cache lookup/store; adjust confidence on partial failures.
- Caching: diskcache for persistent caching, semantic cache helpers for deduping repeated analyses.
- Rate limiting: slowapi at API layer; keep limits configurable via settings.
- Exports: reports/pdf_generator uses ReportLab and Plotly (via kaleido) for charts; fall back gracefully if rendering fails.
- Dependency boundaries: storage, database, auth, and tools are modules exposing functions/classes to be overridden in tests.

#### 6. Do's and Don'ts
- ✅ Do validate and sanitize all user inputs at API boundary using AnalysisRequestValidator.
- ✅ Do run agents in parallel where possible and catch timeouts to maintain responsiveness.
- ✅ Do structure logs with identifiers (report_id, company) and track metrics for jobs and requests.
- ✅ Do mock external APIs in tests; never rely on network for unit tests.
- ✅ Do keep secrets in Secret Manager or environment variables; prefer signed URLs for report access.
- ✅ Do return partial_success when PDF generation fails but analysis is complete.
- ❌ Don't block the event loop with synchronous heavy work inside async endpoints.
- ❌ Don't hardcode API keys, secrets, or project IDs in code or docs.
- ❌ Don't couple presentation (PDF/visualizations) with analysis logic.
- ❌ Don't throw away partial results if one agent fails—degrade gracefully and adjust confidence.

#### 7. Tools & Dependencies
- Key libraries:
  - FastAPI/uvicorn — API layer
  - Pydantic / pydantic-settings — typing, validation, configuration
  - google-generativeai + instructor — LLM and structured outputs
  - Tavily, pytrends, yfinance, edgartools — data sources
  - diskcache, chromadb — caching and semantic retrieval
  - reportlab, plotly, kaleido — PDF and chart rendering
  - slowapi — rate limiting
  - google-cloud-* (storage, secret-manager, logging, firestore) — GCP integrations
- Setup notes:
  - Define required env vars in config.py (e.g., GEMINI_API_KEY, storage bucket, Firestore credentials).
  - Use cloudbuild.yaml or Dockerfile for Cloud Run; keep min instances low and timeouts aligned with orchestrator.
  - Ensure kaleido is available for Plotly static image export used by PDF generation.

#### 8. Other Notes
- API boundaries: consultantos/api/main.py centralizes CORS, rate limiting, and routers. Keep it thin and declarative.
- Long-running tasks: prefer analyze/async with jobs/queue + worker; background_tasks used for uploads and metadata updates.
- Frontend: Next.js app consumes API; avoid server-side secrets in frontend and rely on signed URLs for downloads.
- Logging/metrics: monitoring.py should expose structured logging and aggregated metrics; use it consistently.
- LLM behavior: prompts and response models should reside in consultants/prompts and models; include few-shot examples where possible.
- Edge cases: when all phase-1 agents fail, return 5xx with actionable error; otherwise return partial results and clearly mark partial in metadata.
