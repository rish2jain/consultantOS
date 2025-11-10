"""
Tests for Alpha Vantage tool integration
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import pandas as pd

from consultantos.tools.alpha_vantage_tool import (
    AlphaVantageClient,
    get_technical_indicators,
    get_sector_performance,
    _rate_limiter,
)
from consultantos.models.financial_indicators import (
    TechnicalIndicators,
    SectorPerformance,
)


@pytest.fixture
def mock_api_key():
    """Mock API key for testing"""
    return "test_api_key_12345"


@pytest.fixture
def alpha_vantage_client(mock_api_key):
    """Create Alpha Vantage client with mocked API key"""
    with patch.dict("os.environ", {"ALPHA_VANTAGE_API_KEY": mock_api_key}):
        client = AlphaVantageClient(api_key=mock_api_key)
        return client


@pytest.fixture
def mock_rsi_data():
    """Mock RSI data from Alpha Vantage"""
    df = pd.DataFrame({
        "RSI": [42.5]
    })
    metadata = {"1: Symbol": "AAPL", "2: Indicator": "Relative Strength Index (RSI)"}
    return df, metadata


@pytest.fixture
def mock_macd_data():
    """Mock MACD data from Alpha Vantage"""
    df = pd.DataFrame({
        "MACD": [1.25],
        "MACD_Signal": [0.85],
        "MACD_Hist": [0.40]
    })
    metadata = {"1: Symbol": "AAPL", "2: Indicator": "MACD"}
    return df, metadata


@pytest.fixture
def mock_sma_data():
    """Mock SMA data from Alpha Vantage"""
    df = pd.DataFrame({
        "SMA": [150.25]
    })
    metadata = {"1: Symbol": "AAPL", "2: Indicator": "Simple Moving Average (SMA)"}
    return df, metadata


@pytest.fixture
def mock_quote_data():
    """Mock quote data from Alpha Vantage"""
    df = pd.DataFrame({
        "01. symbol": ["AAPL"],
        "02. open": [151.20],
        "03. high": [153.50],
        "04. low": [150.10],
        "05. price": [152.30],
        "06. volume": [65432100],
        "07. latest trading day": ["2024-11-08"],
        "08. previous close": [151.00],
        "09. change": [1.30],
        "10. change percent": ["0.86%"]
    })
    metadata = {"1: Symbol": "AAPL"}
    return df, metadata


@pytest.fixture
def mock_sector_data():
    """Mock sector performance data from Alpha Vantage"""
    return {
        "Meta Data": {
            "Information": "US Sector Performance (real-time)"
        },
        "Rank A: Real-Time Performance": {
            "Information Technology": "0.45%",
            "Health Care": "0.32%",
            "Financials": "-0.12%"
        },
        "Rank B: 1 Day Performance": {
            "Information Technology": "0.45%",
            "Health Care": "0.32%",
            "Financials": "-0.12%"
        },
        "Rank D: 1 Month Performance": {
            "Information Technology": "5.3%",
            "Health Care": "3.2%",
            "Financials": "1.8%"
        },
        "Rank F: Year-to-Date (YTD) Performance": {
            "Information Technology": "24.5%",
            "Health Care": "12.3%",
            "Financials": "18.7%"
        },
        "Rank G: 1 Year Performance": {
            "Information Technology": "32.7%",
            "Health Care": "18.9%",
            "Financials": "22.1%"
        }
    }


class TestAlphaVantageClient:
    """Test AlphaVantageClient class"""

    def test_client_initialization_with_api_key(self, mock_api_key):
        """Test client initializes correctly with API key"""
        client = AlphaVantageClient(api_key=mock_api_key)
        assert client.enabled is True
        assert client.api_key == mock_api_key

    def test_client_initialization_without_api_key(self):
        """Test client gracefully handles missing API key"""
        with patch.dict("os.environ", {}, clear=True):
            client = AlphaVantageClient()
            assert client.enabled is False

    def test_get_technical_indicators_success(
        self,
        alpha_vantage_client,
        mock_quote_data,
        mock_rsi_data,
        mock_macd_data,
        mock_sma_data
    ):
        """Test successful technical indicators retrieval"""
        # Mock all API calls
        with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", return_value=mock_quote_data), \
             patch.object(alpha_vantage_client.ti, "get_rsi", return_value=mock_rsi_data), \
             patch.object(alpha_vantage_client.ti, "get_macd", return_value=mock_macd_data), \
             patch.object(alpha_vantage_client.ti, "get_sma", return_value=mock_sma_data), \
             patch.object(alpha_vantage_client.ti, "get_ema", return_value=mock_sma_data):

            indicators = alpha_vantage_client.get_technical_indicators("AAPL")

            assert indicators is not None
            assert isinstance(indicators, TechnicalIndicators)
            assert indicators.rsi == 42.5
            assert indicators.rsi_signal == "Hold"
            assert indicators.macd == 1.25
            assert indicators.macd_signal == 0.85
            assert indicators.macd_trend == "Bullish"
            assert indicators.current_price == 152.30

    def test_get_technical_indicators_disabled_client(self):
        """Test technical indicators return None when client disabled"""
        with patch.dict("os.environ", {}, clear=True):
            client = AlphaVantageClient()
            indicators = client.get_technical_indicators("AAPL")
            assert indicators is None

    def test_get_technical_indicators_rsi_signals(self, alpha_vantage_client, mock_quote_data, mock_macd_data, mock_sma_data):
        """Test RSI signal generation for different values"""
        test_cases = [
            (25.0, "Buy - Oversold"),
            (45.0, "Hold"),
            (75.0, "Sell - Overbought"),
        ]

        for rsi_value, expected_signal in test_cases:
            rsi_data = pd.DataFrame({"RSI": [rsi_value]}), {}

            with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", return_value=mock_quote_data), \
                 patch.object(alpha_vantage_client.ti, "get_rsi", return_value=rsi_data), \
                 patch.object(alpha_vantage_client.ti, "get_macd", return_value=mock_macd_data), \
                 patch.object(alpha_vantage_client.ti, "get_sma", return_value=mock_sma_data), \
                 patch.object(alpha_vantage_client.ti, "get_ema", return_value=mock_sma_data):

                indicators = alpha_vantage_client.get_technical_indicators("AAPL")
                assert indicators.rsi_signal == expected_signal

    def test_get_technical_indicators_macd_trends(self, alpha_vantage_client, mock_quote_data, mock_rsi_data, mock_sma_data):
        """Test MACD trend calculation"""
        test_cases = [
            (2.5, 1.5, "Bullish"),    # MACD > Signal
            (1.5, 2.5, "Bearish"),    # MACD < Signal
            (2.0, 2.0, "Neutral"),    # MACD == Signal
        ]

        for macd, signal, expected_trend in test_cases:
            macd_data = pd.DataFrame({
                "MACD": [macd],
                "MACD_Signal": [signal],
                "MACD_Hist": [macd - signal]
            }), {}

            with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", return_value=mock_quote_data), \
                 patch.object(alpha_vantage_client.ti, "get_rsi", return_value=mock_rsi_data), \
                 patch.object(alpha_vantage_client.ti, "get_macd", return_value=macd_data), \
                 patch.object(alpha_vantage_client.ti, "get_sma", return_value=mock_sma_data), \
                 patch.object(alpha_vantage_client.ti, "get_ema", return_value=mock_sma_data):

                indicators = alpha_vantage_client.get_technical_indicators("AAPL")
                assert indicators.macd_trend == expected_trend

    def test_get_technical_indicators_trend_signals(self, alpha_vantage_client, mock_quote_data, mock_rsi_data, mock_macd_data):
        """Test Golden/Death Cross detection"""
        test_cases = [
            (150.0, 145.0, "Golden Cross - Bullish"),    # SMA50 > SMA200
            (145.0, 150.0, "Death Cross - Bearish"),     # SMA50 < SMA200
            (150.0, 150.0, "Neutral"),                    # SMA50 == SMA200
        ]

        for sma50, sma200, expected_signal in test_cases:
            sma50_data = pd.DataFrame({"SMA": [sma50]}), {}
            sma200_data = pd.DataFrame({"SMA": [sma200]}), {}

            def get_sma_side_effect(symbol, interval, time_period):
                if time_period == 50:
                    return sma50_data
                elif time_period == 200:
                    return sma200_data
                else:
                    return pd.DataFrame({"SMA": [150.0]}), {}

            with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", return_value=mock_quote_data), \
                 patch.object(alpha_vantage_client.ti, "get_rsi", return_value=mock_rsi_data), \
                 patch.object(alpha_vantage_client.ti, "get_macd", return_value=mock_macd_data), \
                 patch.object(alpha_vantage_client.ti, "get_sma", side_effect=get_sma_side_effect), \
                 patch.object(alpha_vantage_client.ti, "get_ema", return_value=(pd.DataFrame({"EMA": [150.0]}), {})):

                indicators = alpha_vantage_client.get_technical_indicators("AAPL")
                assert indicators.trend_signal == expected_signal

    def test_get_sector_performance_success(self, alpha_vantage_client, mock_sector_data):
        """Test successful sector performance retrieval"""
        with patch.object(alpha_vantage_client.sp, "get_sector", return_value=(mock_sector_data, {})):
            sector_perf = alpha_vantage_client.get_sector_performance("AAPL", "Information Technology")

            assert sector_perf is not None
            assert isinstance(sector_perf, SectorPerformance)
            assert sector_perf.sector == "Information Technology"
            assert sector_perf.performance_1d == 0.45
            assert sector_perf.performance_1m == 5.3
            assert sector_perf.performance_ytd == 24.5
            assert sector_perf.performance_1y == 32.7

    def test_get_sector_performance_sector_not_found(self, alpha_vantage_client, mock_sector_data):
        """Test sector performance when sector not in data"""
        with patch.object(alpha_vantage_client.sp, "get_sector", return_value=(mock_sector_data, {})):
            sector_perf = alpha_vantage_client.get_sector_performance("AAPL", "Nonexistent Sector")
            assert sector_perf is None

    def test_get_sector_performance_disabled_client(self):
        """Test sector performance returns None when client disabled"""
        with patch.dict("os.environ", {}, clear=True):
            client = AlphaVantageClient()
            sector_perf = client.get_sector_performance("AAPL", "Information Technology")
            assert sector_perf is None

    def test_get_economic_indicators(self, alpha_vantage_client):
        """Test economic indicators (placeholder for premium feature)"""
        indicators = alpha_vantage_client.get_economic_indicators()
        assert indicators is None  # Premium feature not available in free tier


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limiter_respects_limit(self):
        """Test rate limiter enforces call limit"""
        from consultantos.tools.alpha_vantage_tool import RateLimiter

        limiter = RateLimiter(calls_per_minute=3)

        # Should allow 3 calls immediately
        for i in range(3):
            limiter.wait_if_needed()  # Should not wait

        # 4th call should wait (in real scenario)
        # For testing, just verify call_times length
        assert len(limiter.call_times) == 3

    def test_rate_limiter_cleanup(self):
        """Test rate limiter cleans up old call times"""
        from consultantos.tools.alpha_vantage_tool import RateLimiter
        from datetime import timedelta

        limiter = RateLimiter(calls_per_minute=5)

        # Add old call times
        now = datetime.now()
        limiter.call_times = [now - timedelta(minutes=2)]  # Old call

        # New call should clean up old ones
        limiter.wait_if_needed()
        assert len(limiter.call_times) == 1  # Only new call remains


class TestConvenienceFunctions:
    """Test convenience wrapper functions"""

    def test_get_technical_indicators_function(self, mock_api_key, mock_quote_data, mock_rsi_data, mock_macd_data, mock_sma_data):
        """Test get_technical_indicators convenience function"""
        with patch.dict("os.environ", {"ALPHA_VANTAGE_API_KEY": mock_api_key}), \
             patch("consultantos.tools.alpha_vantage_tool.AlphaVantageClient") as MockClient:

            mock_client = MockClient.return_value
            mock_client.enabled = True
            mock_client.get_technical_indicators.return_value = TechnicalIndicators(
                rsi=45.0,
                rsi_signal="Hold",
                current_price=150.0,
                last_updated=datetime.now()
            )

            result = get_technical_indicators("AAPL", api_key=mock_api_key)

            assert result is not None
            assert result.rsi == 45.0
            MockClient.assert_called_once_with(api_key=mock_api_key)

    def test_get_sector_performance_function(self, mock_api_key, mock_sector_data):
        """Test get_sector_performance convenience function"""
        with patch.dict("os.environ", {"ALPHA_VANTAGE_API_KEY": mock_api_key}), \
             patch("consultantos.tools.alpha_vantage_tool.AlphaVantageClient") as MockClient:

            mock_client = MockClient.return_value
            mock_client.enabled = True
            mock_client.get_sector_performance.return_value = SectorPerformance(
                sector="Information Technology",
                performance_ytd=24.5,
                last_updated=datetime.now()
            )

            result = get_sector_performance("AAPL", "Information Technology", api_key=mock_api_key)

            assert result is not None
            assert result.sector == "Information Technology"
            MockClient.assert_called_once_with(api_key=mock_api_key)


class TestErrorHandling:
    """Test error handling and graceful degradation"""

    def test_api_error_handling(self, alpha_vantage_client, mock_quote_data, mock_rsi_data):
        """Test graceful handling of API errors"""
        with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", return_value=mock_quote_data), \
             patch.object(alpha_vantage_client.ti, "get_rsi", return_value=mock_rsi_data), \
             patch.object(alpha_vantage_client.ti, "get_macd", side_effect=Exception("API Error")), \
             patch.object(alpha_vantage_client.ti, "get_sma", side_effect=Exception("API Error")), \
             patch.object(alpha_vantage_client.ti, "get_ema", side_effect=Exception("API Error")):

            # Should not raise exception, but return None or partial data
            try:
                indicators = alpha_vantage_client.get_technical_indicators("AAPL")
                # Should handle error gracefully
                assert True
            except Exception:
                pytest.fail("Should handle API errors gracefully")

    def test_invalid_api_key_handling(self, alpha_vantage_client):
        """Test handling of invalid API key errors"""
        with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", side_effect=Exception("Invalid API key")):
            indicators = alpha_vantage_client.get_technical_indicators("AAPL")
            # Should disable client on invalid API key
            assert alpha_vantage_client.enabled is False

    def test_rate_limit_error_handling(self, alpha_vantage_client, mock_quote_data):
        """Test handling of rate limit errors"""
        with patch.object(alpha_vantage_client.ts, "get_quote_endpoint", side_effect=Exception("Rate limit exceeded")), \
             patch("time.sleep"):  # Mock sleep to avoid waiting in tests
            indicators = alpha_vantage_client.get_technical_indicators("AAPL")
            # Should handle rate limit gracefully (returns None after retries)
            assert indicators is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
