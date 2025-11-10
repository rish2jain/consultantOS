"""
Tests for Finnhub API integration tool
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import vcr
from consultantos.tools.finnhub_tool import FinnhubClient, finnhub_tool
from consultantos.models import AnalystRecommendations, NewsSentiment


# VCR configuration for recording/replaying API responses
finnhub_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/vcr_cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
    filter_headers=['Authorization'],
    decode_compressed_response=True
)


class TestFinnhubClient:
    """Test FinnhubClient wrapper class"""

    @pytest.fixture
    def mock_finnhub_client(self):
        """Create mock Finnhub client"""
        with patch('consultantos.tools.finnhub_tool.finnhub') as mock_finnhub:
            mock_finnhub.FINNHUB_AVAILABLE = True
            mock_client = Mock()
            mock_finnhub.Client.return_value = mock_client
            yield mock_client

    @pytest.fixture
    def finnhub_client(self, mock_finnhub_client):
        """Create FinnhubClient instance"""
        return FinnhubClient(api_key="test_api_key")

    def test_client_initialization_success(self, mock_finnhub_client):
        """Test successful client initialization"""
        client = FinnhubClient(api_key="test_api_key")
        assert client.api_key == "test_api_key"
        assert client._client is not None

    def test_client_initialization_no_api_key(self):
        """Test client initialization without API key"""
        client = FinnhubClient()
        assert client.api_key is None

    def test_company_profile_success(self, finnhub_client, mock_finnhub_client):
        """Test successful company profile fetch"""
        # Mock response
        mock_response = {
            "name": "Tesla Inc",
            "marketCapitalization": 800000,
            "shareOutstanding": 1000,
            "country": "US",
            "currency": "USD",
            "exchange": "NASDAQ",
            "ipo": "2010-06-29",
            "weburl": "https://tesla.com",
            "logo": "https://logo.url",
            "finnhubIndustry": "Automobiles"
        }
        mock_finnhub_client.company_profile2.return_value = mock_response

        result = finnhub_client.company_profile("TSLA")

        assert result["symbol"] == "TSLA"
        assert result["name"] == "Tesla Inc"
        assert result["market_cap"] == 800000
        assert result["industry"] == "Automobiles"
        assert result["source"] == "finnhub"
        assert "timestamp" in result

    def test_company_profile_error(self, finnhub_client, mock_finnhub_client):
        """Test company profile fetch with error"""
        mock_finnhub_client.company_profile2.side_effect = Exception("API Error")

        result = finnhub_client.company_profile("INVALID")

        assert "error" in result
        assert result["symbol"] == "INVALID"
        assert "API Error" in result["error"]

    def test_recommendation_trends_success(self, finnhub_client, mock_finnhub_client):
        """Test successful recommendation trends fetch"""
        mock_response = [
            {
                "period": "2024-01",
                "strongBuy": 10,
                "buy": 15,
                "hold": 8,
                "sell": 2,
                "strongSell": 1
            }
        ]
        mock_finnhub_client.recommendation_trends.return_value = mock_response

        result = finnhub_client.recommendation_trends("TSLA")

        assert result["symbol"] == "TSLA"
        assert result["strong_buy"] == 10
        assert result["buy"] == 15
        assert result["hold"] == 8
        assert result["sell"] == 2
        assert result["strong_sell"] == 1
        assert result["total_analysts"] == 36
        assert result["consensus"] == "Buy"  # More buy than sell
        assert result["period"] == "2024-01"

    def test_recommendation_trends_consensus_calculation(self, finnhub_client, mock_finnhub_client):
        """Test consensus calculation logic"""
        # Test Buy consensus
        mock_finnhub_client.recommendation_trends.return_value = [
            {"period": "2024-01", "strongBuy": 10, "buy": 5, "hold": 2, "sell": 0, "strongSell": 0}
        ]
        result = finnhub_client.recommendation_trends("TSLA")
        assert result["consensus"] == "Buy"

        # Test Sell consensus
        mock_finnhub_client.recommendation_trends.return_value = [
            {"period": "2024-01", "strongBuy": 0, "buy": 0, "hold": 2, "sell": 5, "strongSell": 10}
        ]
        result = finnhub_client.recommendation_trends("TSLA")
        assert result["consensus"] == "Sell"

        # Test Hold consensus
        mock_finnhub_client.recommendation_trends.return_value = [
            {"period": "2024-01", "strongBuy": 2, "buy": 3, "hold": 5, "sell": 3, "strongSell": 2}
        ]
        result = finnhub_client.recommendation_trends("TSLA")
        assert result["consensus"] == "Hold"

    def test_company_news_success(self, finnhub_client, mock_finnhub_client):
        """Test successful news fetch"""
        mock_response = [
            {
                "headline": "Tesla announces new model",
                "summary": "Tesla reveals exciting new product",
                "source": "Reuters",
                "url": "https://news.url",
                "datetime": 1234567890,
                "category": "company news"
            },
            {
                "headline": "Tesla stock surges",
                "summary": "Shares gain on strong earnings",
                "source": "Bloomberg",
                "url": "https://news2.url",
                "datetime": 1234567891,
                "category": "top news"
            }
        ]
        mock_finnhub_client.company_news.return_value = mock_response

        result = finnhub_client.company_news("TSLA", days_back=7)

        assert result["symbol"] == "TSLA"
        assert result["articles_count"] == 2
        assert len(result["articles"]) == 2
        assert result["articles"][0]["headline"] == "Tesla announces new model"
        assert "sentiment_score" in result
        assert result["sentiment"] in ["Positive", "Neutral", "Negative"]

    def test_news_sentiment_calculation(self, finnhub_client, mock_finnhub_client):
        """Test news sentiment calculation"""
        # Positive news
        mock_response = [
            {"headline": "Strong growth and profit beat expectations", "summary": "Success", "source": "News", "url": "url", "datetime": 123, "category": "news"}
        ]
        mock_finnhub_client.company_news.return_value = mock_response
        result = finnhub_client.company_news("TSLA")
        assert result["sentiment_score"] > 0

        # Negative news
        mock_response = [
            {"headline": "Layoff concerns and weak sales decline", "summary": "Loss", "source": "News", "url": "url", "datetime": 123, "category": "news"}
        ]
        mock_finnhub_client.company_news.return_value = mock_response
        result = finnhub_client.company_news("TSLA")
        assert result["sentiment_score"] < 0

    def test_earnings_calendar_success(self, finnhub_client, mock_finnhub_client):
        """Test successful earnings calendar fetch"""
        mock_response = {
            "earningsCalendar": [
                {
                    "date": "2024-01-24",
                    "epsActual": 1.19,
                    "epsEstimate": 1.13,
                    "hour": "amc",
                    "quarter": 4,
                    "revenueActual": 25167000000,
                    "revenueEstimate": 25870000000,
                    "symbol": "TSLA",
                    "year": 2023
                }
            ]
        }
        mock_finnhub_client.earnings_calendar.return_value = mock_response

        result = finnhub_client.earnings_calendar("TSLA")

        assert result["symbol"] == "TSLA"
        assert len(result["earnings_data"]) == 1
        assert result["earnings_data"][0]["symbol"] == "TSLA"
        assert result["source"] == "finnhub"

    def test_caching_behavior(self, finnhub_client, mock_finnhub_client):
        """Test that results are cached"""
        mock_response = {"name": "Tesla Inc", "marketCapitalization": 800000}
        mock_finnhub_client.company_profile2.return_value = mock_response

        # First call
        result1 = finnhub_client.company_profile("TSLA")

        # Second call should use cache
        result2 = finnhub_client.company_profile("TSLA")

        # Should only call API once
        assert mock_finnhub_client.company_profile2.call_count == 1
        assert result1 == result2

    def test_error_response_format(self, finnhub_client):
        """Test error response structure"""
        error_response = finnhub_client._error_response("TSLA", "Test error")

        assert error_response["symbol"] == "TSLA"
        assert error_response["error"] == "Test error"
        assert error_response["source"] == "finnhub"
        assert "timestamp" in error_response


class TestFinnhubToolFunction:
    """Test module-level finnhub_tool function"""

    @patch('consultantos.tools.finnhub_tool.FinnhubClient')
    def test_finnhub_tool_success(self, mock_client_class):
        """Test finnhub_tool function with successful data fetch"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock responses
        mock_client.company_profile.return_value = {"name": "Tesla"}
        mock_client.recommendation_trends.return_value = {"consensus": "Buy"}
        mock_client.company_news.return_value = {"sentiment": "Positive"}
        mock_client.earnings_calendar.return_value = {"earnings_data": []}

        result = finnhub_tool("TSLA", api_key="test_key")

        assert result["symbol"] == "TSLA"
        assert result["profile"]["name"] == "Tesla"
        assert result["recommendations"]["consensus"] == "Buy"
        assert result["news"]["sentiment"] == "Positive"
        assert result["source"] == "finnhub"
        assert "timestamp" in result

    @patch('consultantos.tools.finnhub_tool.FinnhubClient')
    @patch('consultantos.tools.finnhub_tool.settings')
    def test_finnhub_tool_uses_config_api_key(self, mock_settings, mock_client_class):
        """Test that finnhub_tool uses config API key when not provided"""
        mock_settings.finnhub_api_key = "config_api_key"
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        mock_client.company_profile.return_value = {}
        mock_client.recommendation_trends.return_value = {}
        mock_client.company_news.return_value = {}
        mock_client.earnings_calendar.return_value = {}

        finnhub_tool("TSLA")

        # Verify client was initialized with config API key
        mock_client_class.assert_called_with(api_key="config_api_key")

    def test_finnhub_tool_no_api_key(self):
        """Test finnhub_tool without API key"""
        with patch('consultantos.tools.finnhub_tool.settings') as mock_settings:
            mock_settings.finnhub_api_key = None

            result = finnhub_tool("TSLA")

            assert "error" in result
            assert "API key not configured" in result["error"]
            assert result["symbol"] == "TSLA"


class TestCrossValidationIntegration:
    """Test cross-validation between Finnhub and other data sources"""

    @patch('consultantos.tools.finnhub_tool.FinnhubClient')
    def test_market_cap_cross_validation(self, mock_client_class):
        """Test market cap cross-validation logic"""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Finnhub returns market cap in millions
        mock_client.company_profile.return_value = {
            "symbol": "TSLA",
            "name": "Tesla Inc",
            "market_cap": 800000,  # 800B in millions
            "source": "finnhub",
            "timestamp": "2024-01-01T00:00:00"
        }

        result = finnhub_tool("TSLA", api_key="test_key")

        # Verify market cap is returned
        assert result["profile"]["market_cap"] == 800000


@pytest.mark.vcr()
def test_finnhub_real_api_call():
    """
    Test with real API call (requires FINNHUB_API_KEY in .env)
    Uses VCR to record/replay responses
    """
    import os
    api_key = os.getenv("FINNHUB_API_KEY")

    if not api_key or api_key == "your_finnhub_api_key_here":
        pytest.skip("FINNHUB_API_KEY not configured for integration test")

    with finnhub_vcr.use_cassette('finnhub_tsla_profile.yaml'):
        client = FinnhubClient(api_key=api_key)
        result = client.company_profile("TSLA")

        assert "error" not in result
        assert result["symbol"] == "TSLA"
        assert result["name"]  # Should have company name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
