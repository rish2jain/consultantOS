# Code Style & Conventions

## Python Conventions
- **Version**: Python 3.11+ with type hints
- **Modules**: `snake_case`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Agent Classes**: Suffix with `Agent` (e.g., `ResearchAgent`)

## Async Patterns
- Agents implement `async execute()` with per-agent timeouts
- Orchestrator uses `asyncio.gather()` with graceful degradation
- Never block event loop with sync I/O in async endpoints
- Offload long tasks to background jobs

## Type Hints & Validation
- All public functions use type hints
- Input validation at API boundary using Pydantic validators
- Structured outputs via Instructor + Pydantic models
- Response models for all API endpoints

## Error Handling
- Convert internal exceptions to HTTPException at API boundary
- Return `partial_success` when PDF fails but analysis completes
- Graceful degradation: adjust confidence when agents fail
- Never leak secrets in error messages
- Include context in logs: `report_id`, `company`, `user_id`

## Naming Patterns
- Agents: `{Purpose}Agent` (e.g., `ResearchAgent`, `FrameworkAgent`)
- Endpoints: `{resource}_endpoints.py` (e.g., `user_endpoints.py`)
- Models: Domain-specific Pydantic models in `consultantos/models/`
- Utils: Functional helpers, no classes

## Testing Standards
- Test files mirror module structure: `tests/` mirrors `consultantos/`
- Test naming: `test_*.py`, `Test*` classes, `test_*` functions
- Mock all external APIs (Tavily, pytrends, yfinance, edgartools)
- Use `FastAPI TestClient` for API tests
- Target ≥80% code coverage
- Async tests use `pytest-asyncio` with `@pytest.mark.asyncio`

## Import Organization
1. Standard library
2. Third-party packages
3. Local modules

## Docstrings
- Use for public APIs and complex logic
- Follow Google style docstrings
- Include Args, Returns, Raises sections

## Frontend Conventions (TypeScript/Next.js)
- **Components**: PascalCase (e.g., `AnalysisForm.tsx`)
- **Files**: kebab-case for utilities, PascalCase for components
- **Hooks**: Prefix with `use` (e.g., `useAnalysis`)
- **Types**: PascalCase interfaces/types
- **ESLint**: next/core-web-vitals config

## Logging
- Use `monitoring.py` for structured logging
- Include context in all logs
- Never log secrets or API keys
- Log levels: DEBUG, INFO, WARNING, ERROR

## Configuration
- Use pydantic-settings for config management
- Environment variables via `.env` file
- Required vars: `TAVILY_API_KEY`, `GEMINI_API_KEY`
- Optional GCP vars: `GCP_PROJECT_ID`, `GOOGLE_APPLICATION_CREDENTIALS`
