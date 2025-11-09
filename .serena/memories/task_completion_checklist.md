# Task Completion Checklist

## Before Committing Code

### 1. Code Quality
- [ ] All type hints are present on public functions
- [ ] No secrets or API keys in code
- [ ] Error handling follows project patterns
- [ ] Logging includes appropriate context
- [ ] Input validation at API boundaries

### 2. Testing
```bash
# Run all tests
pytest tests/ -v

# Check coverage (should be ≥80%)
pytest tests/ --cov=consultantos

# Run specific tests if you modified specific modules
pytest tests/test_agents.py -v
```

### 3. Backend Linting/Formatting
- [ ] Code follows Python naming conventions (snake_case, PascalCase)
- [ ] Imports are organized (stdlib, third-party, local)
- [ ] Async patterns used correctly (no blocking in async functions)
- [ ] Pydantic models for all API inputs/outputs

### 4. Frontend Linting (if frontend changes)
```bash
cd frontend
npm run lint
```

### 5. Documentation
- [ ] Update CLAUDE.md if adding new commands or patterns
- [ ] Update API_Documentation.md for new endpoints
- [ ] Add docstrings for complex functions
- [ ] Update README.md if changing setup process

### 6. Environment Variables
- [ ] New env vars documented in .env.example
- [ ] Default values provided or marked as required
- [ ] No hardcoded secrets in code

### 7. Dependencies
```bash
# If added new packages
pip freeze > requirements.txt

# For frontend
cd frontend && npm install
```

## Before Deploying

### Backend Deployment Checks
- [ ] All tests passing: `pytest tests/ -v`
- [ ] Environment variables configured in deployment
- [ ] Health check endpoint working: `curl localhost:8080/health`
- [ ] API docs accessible: `http://localhost:8080/docs`

### Frontend Deployment Checks
```bash
cd frontend
npm run build  # Should complete without errors
```

### GCP Cloud Run Deployment
```bash
# Ensure env vars are set
gcloud run deploy consultantos \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY}"
```

## Code Review Checklist

### Security
- [ ] No SQL injection vulnerabilities
- [ ] Input validation and sanitization
- [ ] API keys properly managed
- [ ] Rate limiting configured
- [ ] Error messages don't leak sensitive info

### Performance
- [ ] Async operations used for I/O-bound tasks
- [ ] Caching strategy appropriate
- [ ] Database queries optimized
- [ ] Large operations use background jobs

### Architecture
- [ ] Business logic in agents/orchestrator, not API layer
- [ ] Agents inherit from BaseAgent
- [ ] Graceful degradation implemented
- [ ] Proper separation of concerns

### Testing
- [ ] Unit tests for new functionality
- [ ] Integration tests for API endpoints
- [ ] External APIs mocked
- [ ] Edge cases covered

## Git Workflow

### 1. Before Starting
```bash
git status
git branch  # Should be on feature branch, not main/master
```

### 2. During Development
```bash
# Commit incrementally with meaningful messages
git add .
git diff --staged  # Review changes
git commit -m "feat: add framework analysis caching"
```

### 3. Before PR
- [ ] All tests passing
- [ ] Code follows conventions
- [ ] Commit messages are descriptive
- [ ] Branch is up to date with main/master

### Commit Message Format
```
<type>: <description>

Types: feat, fix, docs, style, refactor, test, chore
Examples:
- feat: add Porter's 5 Forces analysis
- fix: correct market data caching logic
- docs: update API documentation for new endpoints
- test: add integration tests for synthesis agent
```

## Common Quality Issues to Check

### Backend
- [ ] Blocking I/O in async functions
- [ ] Missing error handling
- [ ] Hardcoded values instead of config
- [ ] Missing type hints
- [ ] Improper exception handling (too broad catches)

### Frontend
- [ ] Missing TypeScript types (using `any`)
- [ ] Unhandled promise rejections
- [ ] Missing error boundaries
- [ ] Performance issues (unnecessary re-renders)

## When to Use Async vs Sync

### Use Async (`/analyze/async`) for:
- >3 frameworks requested
- Deep analysis depth
- Long-running operations (>30 seconds expected)

### Use Sync (`/analyze`) for:
- Quick analyses
- ≤3 frameworks
- Standard depth
- When user needs immediate results
