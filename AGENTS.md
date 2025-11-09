# Repository Guidelines

## Project Structure & Module Organization
`consultantos/` contains the FastAPI backend: `agents/` house the five specialized analysts, `orchestrator/` coordinates their phases, `tools/` wraps Tavily, Trends, SEC, and market data sources, while `reports/` and `visualizations/` focus on PDF output. API routers sit in `api/`, shared schemas in `models/`, and infra helpers (auth, cache, monitoring, storage) live at the package root. Frontend work lives in `frontend/` (Next.js app, components, public assets).

## Build, Test & Development Commands
```bash
pip install -r requirements.txt            # Install backend deps
uvicorn consultantos.api.main:app --reload # Run API locally on :8000
pytest                                     # Execute backend test suite
cd frontend && npm install && npm run dev  # Start dashboard at :3000
docker build -t consultantos .             # Build Cloud Run-ready image
```

## Coding Style & Naming Conventions
Target Python 3.11 with full typing and concise docstrings per public entry point. Follow PEP 8 (4-space indents, snake_case functions, PascalCase agents ending in `Agent`, UPPER_SNAKE_CASE constants). Keep API layers thin: validate in `api/`, delegate to agents/tools, and reserve `reports/` for presentation. Prefer async/await over manual loops, ensure logging calls carry `report_id`, `company`, and `user_id`, and sanitize any user strings before persistence or logs.

## Testing Guidelines
Pytest is configured via `pytest.ini`; mirror backend modules under `tests/` (e.g., `tests/test_agents.py`, `tests/tools/test_tavily.py`). Mark async flows with `pytest.mark.asyncio`, mock external services at the tool boundary, and target ≥80 % line coverage with emphasis on orchestrator phases, validators, and `/analyze` endpoints. Name fixtures descriptively (`analysis_request`, `mock_tavily_client`) and keep network calls stubbed for repeatability.

## Commit & Pull Request Guidelines
Commits follow the existing short, imperative style (`Initial project setup`, `Add consultant agents`). Keep summaries under ~65 characters, reference workstreams in the description body, and group related file changes. PRs should link the motivating issue, describe the scenario, list test commands/results, and attach screenshots for UI-affecting frontend work. For backend-only PRs, surface new environment variables, migrations, or infra toggles in the checklist so deployment stays predictable.

## Security & Configuration Notes
Never hardcode API keys—load `GEMINI_API_KEY`, `TAVILY_API_KEY`, and Google Cloud creds via env vars consumed by `config.py`. When running locally, prefer sample `.env` files excluded from git; in Cloud Run, use Secret Manager and keep cache directories on ephemeral storage. Review generated PDFs before sharing to ensure no proprietary data leaks.
