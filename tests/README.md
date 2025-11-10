# ConsultantOS Test Suite

Comprehensive testing documentation for ConsultantOS continuous competitive intelligence platform.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [VCR.py API Mocking](#vcrpy-api-mocking)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Troubleshooting](#troubleshooting)

## Overview

ConsultantOS uses a comprehensive test suite with multiple layers:

- **Unit Tests**: Individual component testing (agents, tools, utilities)
- **Integration Tests**: Multi-component workflows (orchestrator, API endpoints)
- **E2E Tests**: Full system behavior (Playwright browser tests)
- **Property-Based Tests**: Hypothesis-driven edge case testing
- **API Mocking**: VCR.py for deterministic external API testing

**Test Frameworks**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `pytest-cov` - Coverage reporting
- `vcrpy` - HTTP interaction recording
- `Faker` - Realistic test data generation
- `hypothesis` - Property-based testing

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and VCR configuration
├── fixtures/
│   ├── vcr_cassettes/            # Recorded HTTP interactions
│   │   ├── research_agent_*.yaml
│   │   ├── financial_agent_*.yaml
│   │   └── market_agent_*.yaml
│   └── __init__.py
├── test_agents.py                # Agent unit tests (with VCR)
├── test_api.py                   # API endpoint tests
├── test_orchestrator.py          # Orchestration integration tests
├── test_models.py                # Pydantic model validation
├── test_tools.py                 # External tool integration
├── test_utils.py                 # Utility function tests
├── test_worker.py                # Background worker tests
├── e2e/                          # End-to-end Playwright tests
└── README.md                     # This file
```

## VCR.py API Mocking

### What is VCR.py?

VCR.py records HTTP interactions and replays them during tests, providing:

- **Deterministic Tests**: Same responses every time
- **Fast Execution**: No real API calls during tests
- **Offline Testing**: Work without internet
- **Cost Reduction**: No API usage costs for testing
- **Data Privacy**: Sensitive data filtered from recordings

### How ConsultantOS Uses VCR

ConsultantOS agents call external APIs:
- **ResearchAgent** → Tavily API (web search)
- **FinancialAgent** → yfinance + SEC EDGAR APIs
- **MarketAgent** → Google Trends API (pytrends)

VCR intercepts these HTTP calls at the network layer and records them as "cassettes" (YAML files).

### VCR Configuration

Global VCR settings in `tests/conftest.py`:

```python
vcr_config = {
    "cassette_library_dir": "tests/fixtures/vcr_cassettes",
    "record_mode": "once",  # Record new, use existing
    "match_on": ["method", "scheme", "host", "port", "path", "query"],
    "filter_headers": ["Authorization", "X-API-Key", "Cookie"],
    "filter_post_data_parameters": ["api_key", "apikey", "key"],
    "before_record_response": scrub_sensitive_data,
    "serializer": "yaml",
}
```

**Record Modes**:
- `once` (default): Record new cassettes, use existing ones
- `new_episodes`: Add new interactions to existing cassettes
- `none`: Never record, use only existing (fail if missing)
- `all`: Always re-record all cassettes

### Using VCR in Tests

#### Method 1: Decorator Pattern (Recommended)

```python
from tests.conftest import use_cassette

class TestResearchAgent:
    @pytest.mark.asyncio
    @use_cassette("research_agent_tesla")
    async def test_execution(self, tesla_test_data):
        agent = ResearchAgent()

        # Mock only LLM responses, VCR handles API calls
        mock_result = CompanyResearch(company_name="Tesla", ...)
        agent.structured_client = Mock()
        agent.structured_client.chat.completions.create = Mock(return_value=mock_result)

        # This will use VCR cassette for Tavily API calls
        result = await agent.execute(tesla_test_data)
        assert result.company_name == "Tesla"
```

#### Method 2: Fixture Pattern

```python
async def test_with_vcr_fixture(vcr_cassette):
    with vcr_cassette:
        # All HTTP calls here will be recorded/replayed
        result = await agent.execute(data)
```

#### Method 3: Manual Context Manager

```python
import vcr

async def test_manual_vcr():
    with vcr.use_cassette('tests/fixtures/vcr_cassettes/my_test.yaml'):
        result = await agent.execute(data)
```

### Recording New Cassettes

#### First Time Setup

1. Ensure API keys are set:
```bash
export TAVILY_API_KEY="your_tavily_key"
export GEMINI_API_KEY="your_gemini_key"
```

2. Run test with recording mode:
```bash
VCR_RECORD_MODE=all pytest tests/test_agents.py::TestResearchAgent::test_execution -v
```

3. VCR will make real API calls and save them to `tests/fixtures/vcr_cassettes/research_agent_tesla.yaml`

#### Updating Existing Cassettes

```bash
# Re-record specific cassette
VCR_RECORD_MODE=all pytest tests/test_agents.py::TestResearchAgent::test_execution -v

# Add new interactions to existing cassette
VCR_RECORD_MODE=new_episodes pytest tests/test_agents.py -v
```

#### Using Existing Cassettes (No Recording)

```bash
# Fail if cassette missing (CI mode)
VCR_RECORD_MODE=none pytest tests/test_agents.py -v

# Default: Use existing, record new
pytest tests/test_agents.py -v
```

### Cassette Structure

Example cassette (`research_agent_tesla_execution.yaml`):

```yaml
interactions:
- request:
    method: POST
    uri: https://api.tavily.com/search
    headers:
      api-key: REDACTED  # Sensitive data filtered
    body:
      query: "Tesla electric vehicles"
  response:
    status:
      code: 200
    body:
      results: [...]
    headers:
      Content-Type: application/json
version: 1
```

### Sensitive Data Filtering

VCR automatically filters sensitive information:

```python
# Configured in conftest.py
filter_headers = ["Authorization", "X-API-Key", "Cookie"]
filter_post_data_parameters = ["api_key", "apikey", "key"]
before_record_response = scrub_sensitive_data
```

**Never commit real API keys to cassettes!**

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run specific test class
pytest tests/test_agents.py::TestResearchAgent -v

# Run specific test method
pytest tests/test_agents.py::TestResearchAgent::test_research_agent_execution -v

# Run with coverage
pytest tests/ --cov=consultantos --cov-report=html

# Run async tests only
pytest tests/ -k "asyncio" -v

# Run fast tests (skip slow integration tests)
pytest tests/ -m "not slow" -v
```

### Environment Variables

```bash
# VCR Configuration
export VCR_RECORD_MODE=once  # once, new_episodes, none, all

# Test Environment
export PYTEST_FAKER_SEED=12345  # Reproducible test data
export LOG_LEVEL=DEBUG  # Verbose test logging

# API Keys (for recording cassettes)
export TAVILY_API_KEY="your_key"
export GEMINI_API_KEY="your_key"
```

### CI/CD Mode

```bash
# Strict mode: fail on missing cassettes, require coverage
VCR_RECORD_MODE=none pytest tests/ --cov=consultantos --cov-fail-under=80
```

## Writing Tests

### Agent Tests with VCR

```python
from tests.conftest import use_cassette

class TestMyAgent:
    @pytest.mark.asyncio
    @use_cassette("my_agent_test_scenario")
    async def test_my_agent(self, tesla_test_data):
        """Test agent with VCR cassette"""
        agent = MyAgent()

        # Mock LLM response (Gemini API)
        mock_result = MyModel(field="value")
        agent.structured_client = Mock()
        agent.structured_client.chat.completions.create = Mock(return_value=mock_result)

        # External API calls use VCR
        result = await agent.execute(tesla_test_data)

        # Assertions
        assert result.field == "value"
```

### Using Test Fixtures

```python
def test_with_fixtures(tesla_test_data, apple_test_data, microsoft_test_data):
    """Test fixtures provide common test data"""
    assert tesla_test_data["company"] == "Tesla"
    assert tesla_test_data["ticker"] == "TSLA"
```

### Property-Based Testing

```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_company_name_validation(company_name):
    """Test all possible company names"""
    result = validate_company_name(company_name)
    assert isinstance(result, bool)
```

### Mocking Best Practices

```python
# ✅ Good: Mock LLM, use VCR for APIs
@use_cassette("test_scenario")
async def test_good():
    agent = ResearchAgent()
    agent.structured_client = Mock()  # Mock Gemini
    # Tavily uses VCR cassette
    result = await agent.execute(data)

# ❌ Bad: Mock everything
async def test_bad():
    with patch('everything'):  # Doesn't test real integration
        result = await agent.execute(data)
```

## Test Coverage

### Coverage Goals

- **Overall**: ≥80% line coverage
- **Critical Paths**: ≥90% (agents, orchestrator, API)
- **Utilities**: ≥85%
- **Models**: ≥75% (validation logic)

### Generating Coverage Reports

```bash
# Terminal report
pytest tests/ --cov=consultantos --cov-report=term-missing

# HTML report (browse at htmlcov/index.html)
pytest tests/ --cov=consultantos --cov-report=html

# XML report (for CI tools)
pytest tests/ --cov=consultantos --cov-report=xml
```

### Coverage Configuration

```ini
# .coveragerc or pyproject.toml
[coverage:run]
source = consultantos
omit =
    */tests/*
    */migrations/*
    */config.py

[coverage:report]
precision = 2
show_missing = True
skip_covered = False
```

## Troubleshooting

### VCR Issues

#### Cassette Not Found
```
ERROR: Could not find cassette 'research_agent_tesla_execution.yaml'
```
**Solution**: Record the cassette
```bash
VCR_RECORD_MODE=all pytest tests/test_agents.py::test_name -v
```

#### Cassette Mismatch
```
VCRError: Could not find a match for request
```
**Solution**: Request changed, re-record cassette
```bash
rm tests/fixtures/vcr_cassettes/cassette_name.yaml
VCR_RECORD_MODE=all pytest tests/test_agents.py::test_name -v
```

#### Sensitive Data in Cassettes
```
WARNING: API key found in cassette
```
**Solution**: Ensure `scrub_sensitive_data` is working
```python
# Check conftest.py has proper filtering
filter_headers = ["Authorization", "X-API-Key"]
```

### Import Errors

```
ModuleNotFoundError: No module named 'consultantos'
```
**Solution**: Install in development mode
```bash
pip install -e .
# or
pip install -r requirements.txt
```

### Async Test Failures

```
RuntimeError: asyncio.run() cannot be called from a running event loop
```
**Solution**: Use `@pytest.mark.asyncio` and pytest-asyncio
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_operation()
```

### Faker/Hypothesis Conflicts

```
Faker seed not deterministic
```
**Solution**: Set environment variable
```bash
export PYTEST_FAKER_SEED=12345
pytest tests/
```

## Best Practices

### 1. Test Isolation
- Each test should be independent
- Use fixtures for shared setup
- Clean up resources in teardown

### 2. VCR Cassette Management
- Commit cassettes to version control
- Use descriptive cassette names
- Re-record when APIs change
- Filter sensitive data

### 3. Test Data
- Use fixtures for common data (`tesla_test_data`)
- Use Faker for realistic data
- Use Hypothesis for edge cases

### 4. Coverage Targets
- Aim for ≥80% overall coverage
- Focus on critical business logic
- Don't chase 100% coverage

### 5. Test Performance
- Use VCR to avoid slow API calls
- Mark slow tests with `@pytest.mark.slow`
- Run fast tests frequently, slow tests in CI

## Additional Resources

- [VCR.py Documentation](https://vcrpy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-Asyncio Guide](https://github.com/pytest-dev/pytest-asyncio)
- [Faker Documentation](https://faker.readthedocs.io/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)

## Contributing Tests

When adding new tests:

1. **Write the test** with VCR decorator
2. **Record cassettes** with `VCR_RECORD_MODE=all`
3. **Review cassettes** for sensitive data
4. **Run test suite** to ensure no breakage
5. **Check coverage** with `pytest --cov`
6. **Commit cassettes** along with test code

Questions? See [CONTRIBUTING.md](../CONTRIBUTING.md) or open an issue.
