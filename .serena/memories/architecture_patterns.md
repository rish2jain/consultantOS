# Architecture Patterns & Design Guidelines

## Core Architectural Patterns

### 1. BaseAgent Pattern
All agents inherit from `BaseAgent` which provides:
- Gemini + Instructor setup for structured outputs
- Timeout handling (per-agent timeouts)
- Error logging with context
- Consistent interface via `async execute()`

**Implementation**:
```python
class ResearchAgent(BaseAgent):
    async def _execute_internal(self, **kwargs) -> ResearchResult:
        # Agent-specific logic
        pass
```

**Key Rules**:
- Business logic in `_execute_internal()`
- Return Pydantic models for type safety
- Use structured outputs via Instructor
- Handle timeouts gracefully

### 2. Multi-Phase Orchestration

**Execution Model**:
1. **Phase 1 (Parallel)**: Research, Market, Financial agents run concurrently
2. **Phase 2 (Sequential)**: Framework agent applies business frameworks
3. **Phase 3**: Synthesis agent creates executive summary
4. **PDF Generation**: ReportLab + Plotly for visualizations

**Orchestrator Pattern**:
```python
# Phase 1: Parallel execution
results = await asyncio.gather(
    research_agent.execute(),
    market_agent.execute(),
    financial_agent.execute(),
    return_exceptions=True
)

# Phase 2: Sequential with dependencies
framework_result = await framework_agent.execute(
    research=results[0],
    market=results[1],
    financial=results[2]
)
```

**Graceful Degradation**:
- Partial results returned if some agents fail
- Confidence scores adjusted based on available data
- Never fail completely - return what's possible

### 3. Multi-Level Caching

**Cache Hierarchy**:
1. **Disk Cache** (diskcache): Persistent across sessions
2. **Semantic Cache**: Deduplicate similar analyses
3. **Memory Cache**: In-process for frequently accessed data

**Cache Strategy**:
```python
# Check cache before expensive operations
cache_key = f"analysis:{company}:{industry}:{frameworks}"
if cached_result := cache.get(cache_key):
    return cached_result

# Perform analysis
result = await orchestrator.analyze(...)

# Store in cache
cache.set(cache_key, result, expire=3600)
```

**Semantic Caching**:
- Use embedding similarity for company/industry queries
- Threshold: 0.85 similarity to consider cache hit
- Invalidate on framework changes or time decay

### 4. Thin API Layer

**Responsibility**: Validation, authentication, delegation ONLY

**Pattern**:
```python
@router.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    # 1. Validate input
    validated = AnalysisRequestValidator.validate(request)
    
    # 2. Check authentication (if required)
    user = await auth.get_user(api_key)
    
    # 3. Delegate to business logic
    result = await orchestrator.analyze(validated)
    
    # 4. Return response
    return AnalysisResponse(**result)
```

**Anti-pattern**: Business logic in API endpoints

### 5. Structured Outputs

**Use Instructor + Pydantic for all LLM responses**:
```python
from instructor import patch
from pydantic import BaseModel

class PorterAnalysis(BaseModel):
    competitive_rivalry: str
    supplier_power: str
    buyer_power: str
    threat_of_substitutes: str
    threat_of_new_entrants: str

# Structured extraction
client = patch(genai.GenerativeModel())
result = client.chat.completions.create(
    model="gemini-1.5-pro",
    response_model=PorterAnalysis,
    messages=[...]
)
```

**Benefits**:
- Type safety
- Automatic validation
- Consistent response structure
- Easier testing

### 6. Async-First Design

**Rules**:
- All I/O operations are async
- Agents implement `async execute()`
- Orchestrator uses `asyncio.gather()` for parallelism
- Never block event loop with sync I/O

**Background Jobs for Long Operations**:
```python
# Sync endpoint: < 30 seconds
@router.post("/analyze")
async def analyze_sync(request: AnalysisRequest):
    result = await orchestrator.analyze(request)
    return result

# Async endpoint: > 30 seconds
@router.post("/analyze/async")
async def analyze_async(request: AnalysisRequest):
    job_id = await job_queue.enqueue(orchestrator.analyze, request)
    return {"job_id": job_id}
```

### 7. Error Handling Strategy

**Principles**:
- Convert exceptions to HTTPException at API boundary
- Return partial_success when possible
- Include context in all error logs
- Never leak secrets or internal details

**Pattern**:
```python
try:
    result = await orchestrator.analyze(request)
    return AnalysisResponse(status="success", data=result)
except ValidationError as e:
    raise HTTPException(status_code=400, detail="Invalid input")
except TimeoutError:
    return AnalysisResponse(
        status="partial_success",
        data=partial_result,
        confidence=0.6
    )
except Exception as e:
    logger.error("Analysis failed", extra={"company": company, "error": str(e)})
    raise HTTPException(status_code=500, detail="Internal error")
```

### 8. Dependency Injection

**Optional Services Pattern**:
```python
# Define optional dependencies
def get_storage_service():
    if GCP_PROJECT_ID:
        return CloudStorageService()
    return LocalStorageService()

# Use in endpoints
@router.post("/analyze")
async def analyze(
    request: AnalysisRequest,
    storage: StorageService = Depends(get_storage_service)
):
    # Use storage service
    pass
```

**Benefits**:
- Easy testing with mocks
- Flexible deployment (local vs cloud)
- Clean separation of concerns

## Design Guidelines

### Data Flow
```
User Input (API)
    ↓
Validation & Authentication (API Layer)
    ↓
Business Logic (Agents/Orchestrator)
    ↓
External Data (Tools/Cache)
    ↓
Analysis Results
    ↓
Report Generation (Reports/Visualizations)
    ↓
Storage & Response
```

### Separation of Concerns

**DO**:
- Business logic in agents/orchestrator
- Presentation logic in reports/visualizations
- Data access in tools/cache/database/storage
- API layer for validation and routing only

**DON'T**:
- Mix business logic in API endpoints
- Put data access in agents (use tools instead)
- Include presentation logic in business layer

### Testing Strategy

**Unit Tests**: Agents, validators, tools (≥80% coverage)
- Mock external APIs
- Test edge cases
- Verify error handling

**Integration Tests**: Orchestrator, API endpoints
- Mock external services (Tavily, Gemini)
- Test phase execution
- Verify graceful degradation

**Contract Tests**: API schemas, Pydantic models
- Request/response validation
- Schema versioning
- Backward compatibility

### Configuration Management

**Use pydantic-settings**:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    gemini_api_key: str
    tavily_api_key: str
    gcp_project_id: str | None = None
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
```

**Benefits**:
- Type validation
- Environment variable mapping
- Default values
- Easy testing overrides

## Performance Patterns

### Parallel Execution
- Use `asyncio.gather()` for independent operations
- Agents in Phase 1 run concurrently
- Use `return_exceptions=True` for graceful failures

### Caching Strategy
- Cache expensive operations (API calls, LLM responses)
- Use semantic similarity for fuzzy matching
- Implement cache invalidation on updates

### Resource Management
- Per-agent timeouts prevent hangs
- Rate limiting protects against abuse
- Circuit breakers for external services

## Security Patterns

### Input Validation
- Validate all inputs at API boundary
- Sanitize strings before processing
- Use Pydantic validators

### API Key Management
- Optional authentication via headers/query params
- Never log or expose API keys
- Use Secret Manager in production

### Rate Limiting
- slowapi for request rate limiting
- Default: 10 requests/hour per IP
- Configurable via environment variable

## Observability

### Structured Logging
```python
import structlog

logger = structlog.get_logger()
logger.info("analysis_started", 
    company=company, 
    frameworks=frameworks,
    user_id=user_id
)
```

### Metrics to Track
- Request latency
- Agent execution time
- Cache hit rates
- Error rates by endpoint
- Framework usage distribution

### Health Monitoring
- `/health` endpoint for readiness checks
- Database connectivity checks
- External API availability
