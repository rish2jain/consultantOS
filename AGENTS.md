# Repository Guidelines

## Project Structure & Module Organization
`consultantos/` hosts the FastAPI backend: `agents/` implements the five analyst agents, `orchestrator/` sequences their phases, `tools/` wraps Tavily, Trends, SEC, and market data clients, while `reports/` and `visualizations/` handle PDF and dashboard output. Shared API routers live in `api/`, schemas in `models/`, and cross-cutting helpers (auth, cache, logging) sit at the package root. The Next.js dashboard resides in `frontend/`, with UI primitives in `frontend/components` and static assets under `frontend/public`. Tests mirror code under `tests/` and `frontend/__tests__`.

## Build, Test & Development Commands
```bash
pip install -r requirements.txt            # Sync backend deps
uvicorn consultantos.api.main:app --reload # Run API on :8000
pytest                                     # Backend test suite
cd frontend && npm install && npm run dev  # Dashboard on :3000
npm run lint                               # Frontend lint (Next.js defaults)
docker build -t consultantos .             # Cloud Run image
```

## Coding Style & Naming Conventions
Target Python 3.11 with 4-space indents, type hints, concise docstrings, and PascalCase agents ending with `Agent`. Enforce snake_case for functions, UpperCamelCase for Pydantic models, and UPPER_SNAKE_CASE for constants. Prefer async/await, keep routers thin, and include `report_id`, `company`, and `user_id` in each log. Frontend code uses TypeScript with ESLint + Prettier defaults; style components via CSS modules or Tailwind utilities.

## Testing Guidelines
Pytest governs backend coverage; mirror module layout (e.g., `tests/test_agents.py`). Mark async flows with `pytest.mark.asyncio`, stub network calls at the tool boundary, and keep line coverage ≥80%, with extra focus on orchestrator phases and `/analyze`. Frontend tests run via `npm test` (Jest + Testing Library); snapshot only stable UI and favor interaction checks. Store fixtures under `tests/fixtures` with descriptive names like `analysis_request`.

## Commit & Pull Request Guidelines
Write short, imperative commit titles under ~65 characters ("Add consultant agents", "Fix Tavily retry"). Keep related edits together and reference workstreams in the body. PRs must link the motivating issue, describe the scenario plus verification steps, list commands executed, and include screenshots for UI-visible deltas. Call out any new env vars, migrations, or infra toggles so Cloud Run deploys stay predictable.

## Security & Configuration Tips
Never hardcode API keys; load `GEMINI_API_KEY`, `TAVILY_API_KEY`, and Google Cloud creds through `config.py` and local `.env` files ignored by git. In Cloud Run, source secrets from Secret Manager and keep cache storage ephemeral. Review generated PDFs before sharing, and sanitize every user string before persistence or logging.
