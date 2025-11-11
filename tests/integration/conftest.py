"""
Integration test configuration and fixtures
"""
import os
import pytest
import asyncio
from httpx import AsyncClient
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock

# Import application
from consultantos.api.main import app
from consultantos.orchestrator.orchestrator import AnalysisOrchestrator


# ============================================================================
# TEST CLIENT FIXTURES
# ============================================================================

@pytest.fixture
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP test client for API integration tests.

    Yields:
        Configured AsyncClient for testing API endpoints
    """
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def sync_test_client() -> Generator:
    """
    Synchronous HTTP test client for non-async tests.

    Yields:
        TestClient for synchronous API testing
    """
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client


# ============================================================================
# TEST DATA FIXTURES
# ============================================================================

@pytest.fixture
def test_analysis_data() -> dict:
    """
    Standard analysis request data for testing.

    Returns:
        Sample analysis request dictionary
    """
    return {
        "company": "Tesla",
        "industry": "Electric Vehicles",
        "frameworks": ["porter", "swot"],
        "enable_forecasting": True,
        "enable_social_media": True
    }


@pytest.fixture
def test_companies() -> list:
    """
    List of test companies for batch testing.

    Returns:
        List of company data dictionaries
    """
    return [
        {"company": "Tesla", "industry": "Electric Vehicles", "ticker": "TSLA"},
        {"company": "Apple", "industry": "Consumer Electronics", "ticker": "AAPL"},
        {"company": "Microsoft", "industry": "Software", "ticker": "MSFT"},
    ]


@pytest.fixture
def test_forecasting_data() -> dict:
    """
    Sample forecasting request data.

    Returns:
        Forecasting request dictionary
    """
    return {
        "company": "Tesla",
        "metric_name": "Revenue",
        "forecast_horizon_days": 90
    }


@pytest.fixture
def test_wargaming_scenario() -> dict:
    """
    Sample wargaming scenario data.

    Returns:
        Wargaming scenario dictionary
    """
    return {
        "name": "Revenue Scenarios",
        "variables": {
            "revenue": {
                "type": "normal",
                "params": {
                    "mean": 50000000,
                    "std": 5000000
                }
            }
        },
        "formula": "revenue * 0.4 - 10000000"
    }


# ============================================================================
# ORCHESTRATOR FIXTURES
# ============================================================================

@pytest.fixture
def orchestrator() -> AnalysisOrchestrator:
    """
    Analysis orchestrator instance for testing.

    Returns:
        AnalysisOrchestrator instance
    """
    return AnalysisOrchestrator()


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_gemini_client():
    """
    Mock Gemini AI client for testing without API calls.

    Returns:
        Mock client with standard responses
    """
    mock = AsyncMock()
    mock.generate_content.return_value = Mock(
        text="Mock AI response",
        safety_ratings=[],
        finish_reason="STOP"
    )
    return mock


@pytest.fixture
def mock_tavily_client():
    """
    Mock Tavily search client for testing without API calls.

    Returns:
        Mock client with standard search results
    """
    mock = Mock()
    mock.search.return_value = {
        "results": [
            {
                "title": "Test Result",
                "url": "https://example.com",
                "content": "Test content",
                "score": 0.95
            }
        ]
    }
    return mock


@pytest.fixture
def mock_firestore_client():
    """
    Mock Firestore client for testing without database.

    Returns:
        Mock Firestore client
    """
    mock = Mock()
    mock.collection.return_value.document.return_value.set = AsyncMock()
    mock.collection.return_value.document.return_value.get = AsyncMock(
        return_value=Mock(exists=True, to_dict=lambda: {"test": "data"})
    )
    return mock


# ============================================================================
# API KEY HELPERS
# ============================================================================

def has_api_keys() -> bool:
    """
    Check if required API keys are configured.

    Returns:
        True if real API keys are available for integration testing
    """
    required_keys = ["TAVILY_API_KEY", "GEMINI_API_KEY"]
    return all(
        os.getenv(key) and not os.getenv(key).startswith("test_")
        for key in required_keys
    )


def has_social_media_keys() -> bool:
    """
    Check if social media API keys are configured.

    Returns:
        True if Twitter/Reddit API keys are available
    """
    twitter_keys = ["TWITTER_API_KEY", "TWITTER_API_SECRET"]
    reddit_keys = ["REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USER_AGENT"]

    return (
        all(os.getenv(key) for key in twitter_keys) or
        all(os.getenv(key) for key in reddit_keys)
    )


# ============================================================================
# DATABASE FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def setup_test_database():
    """
    Setup test Firestore environment.

    Uses Firestore emulator if available, otherwise uses test project.
    """
    # Check if emulator is running
    emulator_host = os.getenv("FIRESTORE_EMULATOR_HOST")

    if not emulator_host:
        # Use test project or skip
        test_project = os.getenv("TEST_GCP_PROJECT_ID")
        if test_project:
            os.environ["GCP_PROJECT_ID"] = test_project

    yield

    # Cleanup test data
    # (In production, you'd clean up test collections here)


@pytest.fixture
async def cleanup_test_data():
    """
    Cleanup test data after each test.

    Yields control to test, then cleans up.
    """
    yield
    # Cleanup logic here if needed
    # For now, relying on test isolation


# ============================================================================
# LOAD TESTING HELPERS
# ============================================================================

@pytest.fixture
def load_test_config() -> dict:
    """
    Configuration for load testing.

    Returns:
        Load test parameters
    """
    return {
        "concurrent_requests": int(os.getenv("LOAD_TEST_CONCURRENT", "20")),
        "request_timeout": int(os.getenv("LOAD_TEST_TIMEOUT", "60")),
        "ramp_up_time": int(os.getenv("LOAD_TEST_RAMP_UP", "5"))
    }


# ============================================================================
# SKIP MARKERS
# ============================================================================

skip_if_no_api_keys = pytest.mark.skipif(
    not has_api_keys(),
    reason="Real API keys not configured"
)

skip_if_no_social_media = pytest.mark.skipif(
    not has_social_media_keys(),
    reason="Social media API keys not configured"
)

skip_if_no_firestore = pytest.mark.skipif(
    not os.getenv("FIRESTORE_EMULATOR_HOST") and not os.getenv("TEST_GCP_PROJECT_ID"),
    reason="Firestore not configured for testing"
)
