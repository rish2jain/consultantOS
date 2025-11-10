# Integration Testing Guide

Comprehensive integration testing suite for ConsultantOS with 84+ tests covering all major workflows and system integrations.

## Overview

The integration testing suite validates:
- End-to-end user workflows
- Multi-agent orchestration and data flow
- Database operations and persistence
- API endpoints and error handling
- External service integrations
- Load handling and performance
- System resilience and graceful degradation

## Test Organization

```
tests/integration/
├── __init__.py                      # Package initialization
├── conftest.py                      # Test configuration and fixtures
├── test_e2e_workflows.py           # End-to-end workflow tests (15 tests)
├── test_agent_interactions.py      # Agent coordination tests (14 tests)
├── test_database_integration.py    # Database operations (16 tests)
├── test_api_integration.py         # API endpoint tests (20 tests)
├── test_external_services.py       # External API integration (14 tests)
└── test_load.py                    # Load and stress tests (15 tests)
```

## Test Coverage

### 1. End-to-End Workflows (15 tests)

**Primary User Journeys**:
- ✅ Basic analysis workflow (request → analysis → response)
- ✅ Comprehensive analysis with all features enabled
- ✅ Async analysis workflow (enqueue → status → retrieve)
- ✅ Analysis to PDF export workflow
- ✅ Monitoring workflow (NEW: continuous intelligence)
- ✅ Forecasting to wargaming data flow
- ✅ Analysis enhancement workflow
- ✅ Collaborative analysis (share → comment → update)

**Error Handling**:
- ✅ Partial failure graceful degradation
- ✅ Timeout handling workflow
- ✅ Multi-format export (PDF, Excel, Word, JSON)

**Data Flows**:
- ✅ Research to framework data flow
- ✅ Social media to dashboard integration

### 2. Agent Interactions (14 tests)

**Orchestration**:
- ✅ All agents can execute independently
- ✅ Orchestrator phase execution (Phase 1 parallel, Phase 2/3 sequential)
- ✅ Orchestrator graceful degradation on agent failures

**Data Sharing**:
- ✅ Research to framework data flow
- ✅ Market and financial data integration
- ✅ Synthesis agent combines all data sources

**Resilience**:
- ✅ Agent timeout handling
- ✅ Agent retry on transient failures
- ✅ Agent result caching
- ✅ Error propagation with context

**Configuration**:
- ✅ Multiple framework execution
- ✅ Analysis depth parameter handling

### 3. Database Integration (16 tests)

**Firestore Operations**:
- ✅ Analysis storage and retrieval
- ✅ Analysis updates
- ✅ Analysis deletion
- ✅ Query by user ID
- ✅ Query by company name

**Conversation History**:
- ✅ Multi-message conversation persistence
- ✅ Conversation retrieval

**Monitoring Data**:
- ✅ Monitor storage and retrieval
- ✅ Alert storage
- ✅ Snapshot storage for change detection
- ✅ Snapshot comparison

**User Data**:
- ✅ User profile storage and updates
- ✅ Preference management

**Advanced Operations**:
- ✅ Transaction rollback
- ✅ Batch write operations

### 4. API Integration (20 tests)

**Health Checks**:
- ✅ All health endpoints accessible

**Analysis Endpoints**:
- ✅ Input validation (missing/empty fields)
- ✅ Invalid framework handling
- ✅ Successful analysis request
- ✅ Async analysis endpoint

**Job Management**:
- ✅ Job status checking
- ✅ Job completion tracking

**Export Endpoints**:
- ✅ PDF export
- ✅ JSON export
- ✅ Excel export
- ✅ Word export

**Error Handling**:
- ✅ Validation errors (422)
- ✅ Not found errors (404)
- ✅ Method not allowed (405)

**Infrastructure**:
- ✅ CORS headers
- ✅ Request ID tracing
- ✅ Rate limiting
- ✅ Optional authentication
- ✅ API key authentication

**Monitoring**:
- ✅ Monitor creation endpoint
- ✅ Alerts listing endpoint
- ✅ Pagination support

### 5. External Services (14 tests)

**Search & AI** (Requires API keys):
- ✅ Tavily search integration
- ✅ Tavily error handling
- ✅ Gemini AI completion
- ✅ Gemini structured output (Instructor + Pydantic)

**Social Media** (Requires API keys):
- ✅ Twitter search integration
- ✅ Reddit search integration

**Financial Data**:
- ✅ yfinance integration (no API key required)
- ✅ SEC EDGAR filings

**Market Data**:
- ✅ Google Trends integration

**Cloud Services** (Requires GCP):
- ✅ Cloud Storage operations
- ✅ Firestore operations

**Resilience**:
- ✅ Rate limiting handling
- ✅ Circuit breaker pattern
- ✅ Retry logic with backoff

### 6. Load & Stress Tests (15 tests)

**Concurrent Requests**:
- ✅ 20 concurrent analysis requests
- ✅ Mixed endpoint concurrent requests

**Throughput**:
- ✅ Sequential request baseline
- ✅ Parallel request speedup

**Stress Testing**:
- ✅ 50 rapid-fire requests
- ✅ 100 extreme load requests
- ✅ Large payload handling

**Performance**:
- ✅ Memory stability (100 requests)
- ✅ Cache performance improvement
- ✅ Connection pool efficiency

**Resilience**:
- ✅ Request timeout handling
- ✅ Graceful degradation under load

**Configuration**:
- ✅ Configurable load test parameters

## Running Tests

### Quick Start

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with coverage
pytest tests/integration/ --cov=consultantos --cov-report=html

# Run specific test file
pytest tests/integration/test_e2e_workflows.py -v

# Run specific test
pytest tests/integration/test_api_integration.py::test_analyze_endpoint_success -v
```

### Environment Setup

**Required Environment Variables**:
```bash
# Minimum for basic tests (mocked)
TAVILY_API_KEY=test_key
GEMINI_API_KEY=test_key
```

**Optional for Real API Tests**:
```bash
# Real API integration tests
TAVILY_API_KEY=your_real_tavily_key
GEMINI_API_KEY=your_real_gemini_key

# Social media tests
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=your_user_agent

# Database tests
FIRESTORE_EMULATOR_HOST=localhost:8080  # OR
TEST_GCP_PROJECT_ID=your_test_project

# Cloud Storage tests
GCP_PROJECT_ID=your_project_id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Load Test Configuration**:
```bash
LOAD_TEST_CONCURRENT=20      # Concurrent requests (default: 20)
LOAD_TEST_TIMEOUT=60         # Timeout in seconds (default: 60)
LOAD_TEST_RAMP_UP=5          # Ramp up time (default: 5)
```

### Test Markers

```bash
# Run only integration tests
pytest -m integration

# Skip tests requiring real API keys
pytest tests/integration/ -m "not external_api"

# Run only fast tests (skip load tests)
pytest tests/integration/ -k "not load"
```

### CI/CD Integration

**GitHub Actions Example**:
```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov httpx

      - name: Run integration tests
        env:
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          pytest tests/integration/ -v --cov=consultantos --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Fixtures

### Common Fixtures (from conftest.py)

**HTTP Clients**:
- `test_client` - AsyncClient for async API testing
- `sync_test_client` - TestClient for sync testing

**Test Data**:
- `test_analysis_data` - Standard analysis request
- `test_companies` - List of test companies
- `test_forecasting_data` - Forecasting request data
- `test_wargaming_scenario` - Wargaming scenario data

**Mocks**:
- `mock_gemini_client` - Mock AI client
- `mock_tavily_client` - Mock search client
- `mock_firestore_client` - Mock database client

**Helpers**:
- `has_api_keys()` - Check if real API keys are available
- `has_social_media_keys()` - Check social media credentials
- `setup_test_database` - Configure test database

**Skip Markers**:
- `skip_if_no_api_keys` - Skip if no real API keys
- `skip_if_no_social_media` - Skip if no social media keys
- `skip_if_no_firestore` - Skip if Firestore not configured

## Best Practices

### 1. Test-Driven Development (TDD)

**Red-Green-Refactor**:
```python
# 1. Write failing test first
@pytest.mark.asyncio
async def test_new_feature(test_client):
    response = await test_client.post("/new-feature", json={...})
    assert response.status_code == 200  # FAILS initially

# 2. Implement minimal code to pass
# 3. Refactor with tests as safety net
```

### 2. Mocking External Services

**Always mock in integration tests** (unless specifically testing external APIs):

```python
with patch("consultantos.tools.tavily_tool.TavilyClient") as mock:
    mock.return_value.search.return_value = {...}
    # Test business logic, not external APIs
```

### 3. Test Isolation

Each test should be independent:
- ✅ No shared state between tests
- ✅ Clean up created resources
- ✅ Use unique identifiers (uuid)
- ✅ Reset mocks between tests

### 4. Meaningful Assertions

```python
# ❌ Bad
assert result is not None

# ✅ Good
assert result["company"] == "Tesla"
assert result["confidence_score"] >= 0.8
assert "research" in result
```

### 5. Error Testing

Test both success and failure paths:

```python
# Test validation error
response = await test_client.post("/analyze", json={"company": ""})
assert response.status_code == 422

# Test not found error
response = await test_client.get("/reports/nonexistent")
assert response.status_code == 404
```

## Troubleshooting

### Common Issues

**1. Import Errors**:
```bash
# Ensure ConsultantOS is in Python path
export PYTHONPATH=/Users/rish2jain/Documents/Hackathons/ConsultantOS:$PYTHONPATH
```

**2. Async Tests Failing**:
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio_mode = auto
```

**3. Database Tests Skipped**:
```bash
# Start Firestore emulator
gcloud emulators firestore start --host-port=localhost:8080

# Set environment variable
export FIRESTORE_EMULATOR_HOST=localhost:8080
```

**4. Rate Limiting in Tests**:
```bash
# Use mocks instead of real APIs for faster tests
# Or increase rate limit for testing
export RATE_LIMIT_PER_HOUR=1000
```

### Debug Mode

```bash
# Run with verbose output
pytest tests/integration/ -vv

# Show print statements
pytest tests/integration/ -s

# Stop on first failure
pytest tests/integration/ -x

# Show locals in tracebacks
pytest tests/integration/ -l
```

## Test Results Summary

### Current Status

**Total Tests**: 84 integration tests

**Coverage by Category**:
- End-to-End Workflows: 15 tests ✅
- Agent Interactions: 14 tests ✅
- Database Operations: 16 tests ✅
- API Endpoints: 20 tests ✅
- External Services: 14 tests ✅
- Load & Stress: 15 tests ✅

**Expected Pass Rate**:
- With mocks (default): ~90% pass
- With real APIs: Depends on API availability
- With Firestore: Requires emulator or test project

**Known Limitations**:
- Some endpoints may not be fully implemented yet
- Real API tests require valid credentials
- Database tests require Firestore configuration
- Load tests may be flaky in CI environments

## CI/CD Recommendations

### Pre-Merge Checks

```yaml
# Require these tests to pass before merge
required_tests:
  - test_all_health_endpoints_accessible
  - test_complete_analysis_workflow_basic
  - test_all_agents_can_execute
  - test_analyze_endpoint_validation
  - test_concurrent_analysis_requests
```

### Nightly Tests

```yaml
# Run with real APIs nightly
nightly_tests:
  - test_tavily_search_integration
  - test_gemini_completion_integration
  - test_firestore_integration
  - test_stress_rapid_requests
```

### Performance Benchmarks

```yaml
# Track performance over time
benchmarks:
  - test_sequential_request_throughput
  - test_cache_performance_improvement
  - test_memory_stability_repeated_requests
```

## Future Enhancements

### Planned Additions

1. **Contract Testing**: Pact.io for API contract validation
2. **Chaos Engineering**: Fault injection testing
3. **Security Testing**: OWASP security validation
4. **Accessibility Testing**: WCAG compliance checks
5. **Visual Regression**: Screenshot comparison tests
6. **Mobile Testing**: Responsive design validation
7. **Browser Testing**: Cross-browser compatibility
8. **Mutation Testing**: Test quality assessment

### Monitoring Integration

```python
# Add monitoring to tests
@pytest.mark.asyncio
async def test_with_metrics(test_client):
    with monitor_test_metrics():
        response = await test_client.post("/analyze", ...)
        # Metrics automatically recorded
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [HTTPX AsyncClient](https://www.python-httpx.org/)
- [Hypothesis (Property Testing)](https://hypothesis.readthedocs.io/)
- [Test-Driven Development](https://testdriven.io/)

## Contributing

When adding integration tests:

1. **Follow naming convention**: `test_<feature>_<scenario>`
2. **Add docstrings**: Explain what the test validates
3. **Use appropriate markers**: `@pytest.mark.integration`
4. **Mock external dependencies**: Unless testing integration
5. **Update this documentation**: Keep coverage matrix current
6. **Run tests locally**: Ensure they pass before committing

## Contact

For questions or issues with integration tests:
- Check existing test patterns in `tests/integration/`
- Review fixtures in `conftest.py`
- Consult architecture docs in `ARCHITECTURE.md`
