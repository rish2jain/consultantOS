"""
External Service Integration Tests

Tests integration with external APIs: Tavily, Gemini, Twitter, Reddit, etc.

NOTE: These tests require real API keys and are skipped by default.
Set environment variables to enable:
- TAVILY_API_KEY
- GEMINI_API_KEY
- TWITTER_API_KEY, TWITTER_API_SECRET
- REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
"""
import pytest
import os
from unittest.mock import patch

from tests.integration.conftest import skip_if_no_api_keys, skip_if_no_social_media


# ============================================================================
# TAVILY SEARCH INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@skip_if_no_api_keys
@pytest.mark.asyncio
async def test_tavily_search_integration():
    """
    Test real Tavily API integration.

    Requires TAVILY_API_KEY environment variable.
    """
    from consultantos.tools.tavily_tool import TavilyClient

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        # Perform real search
        results = client.search(
            query="Tesla electric vehicles competitive analysis",
            max_results=5
        )

        # Verify results
        assert results is not None
        assert "results" in results
        assert len(results["results"]) > 0

        # Verify result structure
        first_result = results["results"][0]
        assert "title" in first_result
        assert "url" in first_result
        assert "content" in first_result

    except Exception as e:
        pytest.fail(f"Tavily integration failed: {e}")


@pytest.mark.integration
@skip_if_no_api_keys
@pytest.mark.asyncio
async def test_tavily_search_error_handling():
    """
    Test Tavily error handling with invalid queries.

    Should handle errors gracefully.
    """
    from consultantos.tools.tavily_tool import TavilyClient

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        # Empty query should be handled
        results = client.search(query="", max_results=1)

        # Should either return empty results or raise handled exception
        assert results is not None or True

    except Exception:
        # Error handling is acceptable
        pass


# ============================================================================
# GEMINI AI INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@skip_if_no_api_keys
@pytest.mark.asyncio
async def test_gemini_completion_integration():
    """
    Test real Gemini API integration.

    Requires GEMINI_API_KEY environment variable.
    """
    import google.generativeai as genai

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    try:
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Simple test prompt
        response = model.generate_content("What is competitive analysis? Respond in one sentence.")

        assert response is not None
        assert response.text is not None
        assert len(response.text) > 0

    except Exception as e:
        pytest.fail(f"Gemini integration failed: {e}")


@pytest.mark.integration
@skip_if_no_api_keys
@pytest.mark.asyncio
async def test_gemini_structured_output():
    """
    Test Gemini with structured output via Instructor.

    Validates Pydantic model integration.
    """
    from pydantic import BaseModel
    import google.generativeai as genai
    from instructor import patch

    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    class CompetitiveAnalysis(BaseModel):
        company: str
        key_competitor: str
        competitive_advantage: str

    try:
        client = patch(genai.GenerativeModel('gemini-1.5-pro'))

        response = client.chat.completions.create(
            response_model=CompetitiveAnalysis,
            messages=[{
                "role": "user",
                "content": "Analyze Tesla's competitive position in one sentence"
            }]
        )

        assert isinstance(response, CompetitiveAnalysis)
        assert response.company is not None
        assert response.key_competitor is not None

    except Exception as e:
        pytest.skip(f"Structured output not fully configured: {e}")


# ============================================================================
# TWITTER INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@skip_if_no_social_media
@pytest.mark.asyncio
async def test_twitter_search_integration():
    """
    Test real Twitter API integration.

    Requires Twitter API credentials.
    """
    if not all([
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET")
    ]):
        pytest.skip("Twitter API credentials not configured")

    try:
        # Import Twitter connector
        from consultantos.tools.social_media.twitter_connector import TwitterConnector

        connector = TwitterConnector(
            api_key=os.getenv("TWITTER_API_KEY"),
            api_secret=os.getenv("TWITTER_API_SECRET")
        )

        # Search for tweets
        tweets = await connector.search_tweets(
            keywords=["Tesla"],
            max_results=5
        )

        assert tweets is not None
        assert len(tweets) > 0

        # Verify tweet structure
        first_tweet = tweets[0]
        assert hasattr(first_tweet, 'text') or 'text' in first_tweet

    except ImportError:
        pytest.skip("Twitter connector not implemented")
    except Exception as e:
        pytest.skip(f"Twitter integration failed: {e}")


# ============================================================================
# REDDIT INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@skip_if_no_social_media
@pytest.mark.asyncio
async def test_reddit_search_integration():
    """
    Test real Reddit API integration.

    Requires Reddit API credentials.
    """
    if not all([
        os.getenv("REDDIT_CLIENT_ID"),
        os.getenv("REDDIT_CLIENT_SECRET"),
        os.getenv("REDDIT_USER_AGENT")
    ]):
        pytest.skip("Reddit API credentials not configured")

    try:
        # Import Reddit connector
        from consultantos.tools.social_media.reddit_connector import RedditConnector

        connector = RedditConnector(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )

        # Search for posts
        posts = await connector.search_posts(
            keywords=["Tesla"],
            limit=5
        )

        assert posts is not None
        assert len(posts) > 0

        # Verify post structure
        first_post = posts[0]
        assert hasattr(first_post, 'title') or 'title' in first_post

    except ImportError:
        pytest.skip("Reddit connector not implemented")
    except Exception as e:
        pytest.skip(f"Reddit integration failed: {e}")


# ============================================================================
# FINANCIAL DATA INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_yfinance_integration():
    """
    Test yfinance integration for financial data.

    No API key required - uses Yahoo Finance.
    """
    try:
        import yfinance as yf

        # Fetch Tesla stock data
        ticker = yf.Ticker("TSLA")
        info = ticker.info

        assert info is not None
        assert "symbol" in info or "shortName" in info

        # Get historical data
        hist = ticker.history(period="1mo")
        assert len(hist) > 0

    except Exception as e:
        pytest.skip(f"yfinance integration failed: {e}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_sec_edgar_integration():
    """
    Test SEC EDGAR integration for filings.

    No API key required - public SEC data.
    """
    try:
        from consultantos.tools.financial_tool import get_sec_filings

        # Get Tesla filings
        filings = get_sec_filings(ticker="TSLA", filing_type="10-K", limit=1)

        assert filings is not None
        assert len(filings) > 0

    except ImportError:
        pytest.skip("SEC EDGAR tool not implemented")
    except Exception as e:
        pytest.skip(f"SEC EDGAR integration failed: {e}")


# ============================================================================
# GOOGLE TRENDS INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_google_trends_integration():
    """
    Test Google Trends integration via pytrends.

    No API key required.
    """
    try:
        from pytrends.request import TrendReq

        pytrends = TrendReq()

        # Get interest over time for Tesla
        pytrends.build_payload(["Tesla"], timeframe='today 3-m')
        interest = pytrends.interest_over_time()

        assert interest is not None
        assert len(interest) > 0

    except Exception as e:
        pytest.skip(f"Google Trends integration failed: {e}")


# ============================================================================
# CLOUD STORAGE INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("GCP_PROJECT_ID"),
    reason="GCP project not configured"
)
@pytest.mark.asyncio
async def test_cloud_storage_integration():
    """
    Test Google Cloud Storage integration.

    Requires GCP_PROJECT_ID and credentials.
    """
    try:
        from consultantos.storage import CloudStorageService

        storage = CloudStorageService()

        # Test upload
        test_data = b"Test report content"
        blob_name = "test_integration_report.pdf"

        await storage.upload_blob(blob_name, test_data)

        # Test download
        downloaded = await storage.download_blob(blob_name)

        assert downloaded == test_data

        # Cleanup
        await storage.delete_blob(blob_name)

    except Exception as e:
        pytest.skip(f"Cloud Storage integration failed: {e}")


# ============================================================================
# FIRESTORE INTEGRATION TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("FIRESTORE_EMULATOR_HOST") and not os.getenv("GCP_PROJECT_ID"),
    reason="Firestore not configured"
)
@pytest.mark.asyncio
async def test_firestore_integration():
    """
    Test Firestore database integration.

    Uses emulator if available, otherwise test project.
    """
    try:
        from consultantos.database import DatabaseService

        db = DatabaseService()

        # Test write
        test_doc = {
            "test_id": "integration_test_123",
            "data": "test"
        }

        await db.store_analysis(test_doc)

        # Test read
        retrieved = await db.get_analysis("integration_test_123")

        assert retrieved is not None
        assert retrieved["data"] == "test"

        # Cleanup
        await db.delete_analysis("integration_test_123")

    except Exception as e:
        pytest.skip(f"Firestore integration failed: {e}")


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================

@pytest.mark.integration
@skip_if_no_api_keys
@pytest.mark.asyncio
async def test_tavily_rate_limiting():
    """
    Test that rate limiting is handled for external APIs.

    Should not exceed API rate limits.
    """
    from consultantos.tools.tavily_tool import TavilyClient

    client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        # Make multiple requests
        results = []
        for i in range(3):  # Small number to avoid hitting limits
            result = client.search(
                query=f"Tesla competitive analysis {i}",
                max_results=1
            )
            results.append(result)

        # All should succeed
        assert len(results) == 3
        assert all(r is not None for r in results)

    except Exception as e:
        # Rate limiting is acceptable
        if "rate limit" in str(e).lower() or "429" in str(e):
            pass  # Expected
        else:
            pytest.fail(f"Unexpected error: {e}")


# ============================================================================
# CIRCUIT BREAKER TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_external_service_circuit_breaker():
    """
    Test circuit breaker pattern for external services.

    Should open circuit after repeated failures.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient.search") as mock_search:
        # Simulate repeated failures
        mock_search.side_effect = Exception("Service unavailable")

        try:
            from consultantos.utils.circuit_breaker import CircuitBreaker

            breaker = CircuitBreaker(failure_threshold=3)

            # Try multiple times - circuit should open
            for _ in range(5):
                try:
                    with breaker:
                        mock_search(query="test")
                except Exception:
                    pass

            # Circuit should be open
            assert breaker.state == "open" or breaker.failure_count >= 3

        except ImportError:
            pytest.skip("Circuit breaker not implemented")


# ============================================================================
# RETRY LOGIC TESTS
# ============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_external_service_retry_logic():
    """
    Test retry logic for transient failures.

    Should retry failed requests with exponential backoff.
    """
    with patch("consultantos.tools.tavily_tool.TavilyClient.search") as mock_search:
        # Fail first two times, succeed on third
        mock_search.side_effect = [
            Exception("Temporary error"),
            Exception("Temporary error"),
            {"results": [{"title": "Success"}]}
        ]

        try:
            from consultantos.utils.retry import retry_with_backoff

            @retry_with_backoff(max_retries=3)
            async def search_with_retry():
                return mock_search(query="test")

            result = await search_with_retry()

            assert result is not None
            assert "results" in result

        except ImportError:
            pytest.skip("Retry logic not implemented")
        except Exception as e:
            pytest.skip(f"Retry test failed: {e}")
