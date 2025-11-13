# Repository Guidelines

## Project Structure & Module Organization
`consultantos/` houses the FastAPI backend: `agents/` for ResearchAgent through DarkDataAgent logic, `orchestrator/` for multi-phase sequencing, and `tools/` for Tavily, Google Trends, SEC, and market-data clients. Shared routers live under `api/`, data contracts under `models/`, and PDF/dashboard generators inside `reports/` and `visualizations/`. The Next.js dashboard resides in `frontend/` with reusable UI inside `frontend/components` and static assets in `frontend/public`. Tests mirror this layout via `tests/` for Python modules and `frontend/__tests__/` for UI logic.

## Build, Test & Development Commands
- `pip install -r requirements.txt` — sync backend dependencies.
- `uvicorn consultantos.api.main:app --reload --port 8080` — run the API locally with hot reload.
- `pytest` — execute backend suites; expect ≥80% coverage.
- `cd frontend && npm install && npm run dev` — boot the dashboard on :3000.
- `npm run lint` — enforce Next.js ESLint + Prettier rules.
- `docker build -t consultantos .` — produce the Cloud Run-ready image.

## Coding Style & Naming Conventions
Target Python 3.11, four-space indents, and concise docstrings. Agents and orchestrators end in `Agent`/`Orchestrator`, async functions stay snake_case, Pydantic models use UpperCamelCase, and constants are UPPER_SNAKE_CASE. Log records must include `report_id`, `company`, and `user_id`. Frontend code is TypeScript with functional React components, Tailwind or CSS modules, and colocated hooks/utilities under `frontend/lib`.

## Testing Guidelines
Use `pytest` with `pytest.mark.asyncio` for coroutine flows and stub network calls at the tool boundary. Mirror source names (e.g., `tests/test_orchestrator.py`) and keep fixtures inside `tests/fixtures` with descriptive filenames such as `analysis_request.json`. UI coverage relies on Jest + Testing Library via `npm test`; prefer event-driven assertions over snapshots and include Playwright smoke checks when changing routing.

## Commit & Pull Request Guidelines
Write imperative commit titles under ~65 characters ("Add Tavily retries"). Describe the scenario, major changes, and verification commands in the body, noting new env vars or migrations. PRs must link the driving issue, enumerate commands executed, attach screenshots or recordings for UI-visible work, and explain rollout or feature-flag steps so Cloud Run deploys remain predictable.

## Security & Configuration Tips
Never hardcode `GEMINI_API_KEY`, `TAVILY_API_KEY`, or Google Cloud secrets; pull them through `config.py` and local `.env` files (already git-ignored). Assume Cloud Run storage is ephemeral, scrub user-provided text before logging, and manually review generated PDFs/dashboards before sharing externally.
