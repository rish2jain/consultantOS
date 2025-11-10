# Integration Tests

Comprehensive integration testing suite for ConsultantOS with 84+ tests.

## Quick Start

```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_e2e_workflows.py -v

# Run with coverage
pytest tests/integration/ --cov=consultantos --cov-report=html
```

## Test Structure

```
tests/integration/
├── conftest.py                     # Fixtures and configuration
├── test_e2e_workflows.py          # 15 end-to-end workflow tests
├── test_agent_interactions.py     # 14 agent coordination tests
├── test_database_integration.py   # 16 database operation tests
├── test_api_integration.py        # 20 API endpoint tests
├── test_external_services.py      # 14 external API tests
└── test_load.py                   # 15 load and stress tests
```

## Test Categories

### End-to-End Workflows (15 tests)
- Complete analysis workflows (basic, comprehensive, async)
- Monitoring workflows (NEW continuous intelligence)
- Export workflows (PDF, Excel, Word, JSON)
- Multi-stage workflows (enhancement, collaboration)
- Error recovery and graceful degradation

### Agent Interactions (14 tests)
- Multi-agent orchestration
- Phase execution patterns
- Data sharing and integration
- Timeout and retry mechanisms
- Caching and performance

### Database Integration (16 tests)
- Firestore CRUD operations
- Conversation history persistence
- Monitoring data (monitors, alerts, snapshots)
- User profile management
- Transactions and batch operations

### API Integration (20 tests)
- Health checks and validation
- Analysis endpoints
- Export endpoints (all formats)
- Error handling (422, 404, 405)
- Authentication and rate limiting

### External Services (14 tests)
- Tavily search integration
- Gemini AI with structured outputs
- Social media (Twitter, Reddit)
- Financial data (yfinance, SEC)
- Cloud services (Storage, Firestore)

### Load & Stress (15 tests)
- Concurrent request handling
- Throughput benchmarking
- Memory stability testing
- Stress testing (50-100 requests)
- Cache and connection pooling

## Environment Setup

### Minimum (for mocked tests)
```bash
export TAVILY_API_KEY=test_key
export GEMINI_API_KEY=test_key
```

### Full Integration (optional)
```bash
# Real API testing
export TAVILY_API_KEY=your_real_key
export GEMINI_API_KEY=your_real_key

# Social media
export TWITTER_API_KEY=your_key
export TWITTER_API_SECRET=your_secret
export REDDIT_CLIENT_ID=your_id
export REDDIT_CLIENT_SECRET=your_secret
export REDDIT_USER_AGENT=your_agent

# Database
export FIRESTORE_EMULATOR_HOST=localhost:8080

# Cloud
export GCP_PROJECT_ID=your_project
```

## Running Specific Tests

```bash
# Single test
pytest tests/integration/test_api_integration.py::test_analyze_endpoint_success -v

# Test category
pytest tests/integration/test_load.py -v

# Skip external API tests
pytest tests/integration/ -m "not external_api"

# Debug mode
pytest tests/integration/ -vv -s
```

## CI/CD Integration

```yaml
- name: Run Integration Tests
  run: |
    pytest tests/integration/ -v \
      --cov=consultantos \
      --cov-report=xml
```

## Documentation

See [INTEGRATION_TESTING.md](../../INTEGRATION_TESTING.md) for comprehensive documentation including:
- Detailed test descriptions
- Best practices
- Troubleshooting guide
- CI/CD recommendations
- Future enhancements

## Metrics

- **Total Tests**: 84
- **Total Lines**: 3,243
- **Test Files**: 7
- **Coverage**: Comprehensive system validation

## Support

For issues or questions:
1. Check test docstrings for test purpose
2. Review fixtures in conftest.py
3. Consult INTEGRATION_TESTING.md
4. Check existing test patterns
