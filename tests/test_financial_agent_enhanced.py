"""
Tests for enhanced FinancialAgent with multi-source data and cross-validation
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from consultantos.agents.financial_agent import FinancialAgent
from consultantos.models import (
    FinancialSnapshot,
    AnalystRecommendations,
    NewsSentiment,
    DataSourceValidation
)


class TestFinancialAgentEnhanced:
    """Test enhanced FinancialAgent with Finnhub integration"""

    @pytest.fixture
    def financial_agent(self):
        """Create FinancialAgent instance"""
        return FinancialAgent()

    @pytest.fixture
    def mock_yfinance_data(self):
        """Mock yfinance response"""
        return {
            "company_info": {
                "marketCap": 800_000_000_000,
                "totalRevenue": 96_000_000_000,
                "profitMargins": 0.15,
                "trailingPE": 65.5
            },
            "price_history": {},
            "financials": {},
            "ticker": "TSLA"
        }

    @pytest.fixture
    def mock_finnhub_data(self):
        """Mock Finnhub response"""
        return {
            "symbol": "TSLA",
            "profile": {
                "symbol": "TSLA",
                "name": "Tesla Inc",
                "market_cap": 800000,  # In millions
                "industry": "Automobiles",
                "source": "finnhub"
            },
            "recommendations": {
                "symbol": "TSLA",
                "strong_buy": 10,
                "buy": 15,
                "hold": 8,
                "sell": 2,
                "strong_sell": 1,
                "total_analysts": 36,
                "consensus": "Buy",
                "period": "2024-01"
            },
            "news": {
                "symbol": "TSLA",
                "articles_count": 10,
                "sentiment_score": 0.35,
                "sentiment": "Positive",
                "articles": [
                    {"headline": "Tesla stock surges on strong earnings"},
                    {"headline": "Tesla announces new model"},
                    {"headline": "Tesla expands production capacity"}
                ]
            },
            "earnings": {
                "symbol": "TSLA",
                "earnings_data": []
            },
            "source": "finnhub"
        }

    @pytest.fixture
    def mock_sec_data(self):
        """Mock SEC EDGAR response"""
        return {
            "filing_date": "2024-01-15",
            "filing_type": "10-K",
            "ticker": "TSLA"
        }

    @pytest.mark.asyncio
    async def test_fetch_all_sources_parallel(self, financial_agent, mock_yfinance_data, mock_finnhub_data, mock_sec_data):
        """Test parallel data fetching from all sources"""
        with patch('consultantos.agents.financial_agent.yfinance_tool', return_value=mock_yfinance_data), \
             patch('consultantos.agents.financial_agent.finnhub_tool', return_value=mock_finnhub_data), \
             patch('consultantos.agents.financial_agent.sec_edgar_tool', return_value=mock_sec_data):

            yf_data, fh_data, sec_data = await financial_agent._fetch_all_sources("TSLA")

            assert yf_data == mock_yfinance_data
            assert fh_data == mock_finnhub_data
            assert sec_data == mock_sec_data

    @pytest.mark.asyncio
    async def test_fetch_all_sources_with_errors(self, financial_agent):
        """Test parallel fetching handles errors gracefully"""
        with patch('consultantos.agents.financial_agent.yfinance_tool', side_effect=Exception("yfinance error")), \
             patch('consultantos.agents.financial_agent.finnhub_tool', side_effect=Exception("finnhub error")), \
             patch('consultantos.agents.financial_agent.sec_edgar_tool', side_effect=Exception("sec error")):

            yf_data, fh_data, sec_data = await financial_agent._fetch_all_sources("TSLA")

            assert "error" in yf_data
            assert "error" in fh_data
            assert "error" in sec_data

    def test_cross_validate_sources_success(self, financial_agent, mock_yfinance_data, mock_finnhub_data):
        """Test cross-validation with matching data"""
        validations = financial_agent._cross_validate_sources(mock_yfinance_data, mock_finnhub_data)

        assert len(validations) == 1
        validation = validations[0]

        assert validation.metric == "market_cap"
        assert validation.yfinance_value == 800_000_000_000
        assert validation.finnhub_value == 800_000_000_000  # 800000 * 1M
        assert validation.is_valid is True
        assert validation.discrepancy_pct == 0.0

    def test_cross_validate_sources_discrepancy(self, financial_agent):
        """Test cross-validation with significant discrepancy"""
        yf_data = {
            "company_info": {
                "marketCap": 800_000_000_000  # 800B
            }
        }
        fh_data = {
            "profile": {
                "market_cap": 1_000_000  # 1T in millions (1000B actual)
            }
        }

        validations = financial_agent._cross_validate_sources(yf_data, fh_data)

        assert len(validations) == 1
        validation = validations[0]

        assert validation.metric == "market_cap"
        assert validation.is_valid is False  # 25% discrepancy
        assert validation.discrepancy_pct > 20.0
        assert "threshold" in validation.note.lower()

    def test_cross_validate_sources_skip_on_error(self, financial_agent):
        """Test cross-validation skips when sources have errors"""
        yf_data = {"error": "yfinance failed"}
        fh_data = {"profile": {"market_cap": 800000}}

        validations = financial_agent._cross_validate_sources(yf_data, fh_data)

        assert len(validations) == 0

    def test_extract_analyst_recommendations_success(self, financial_agent, mock_finnhub_data):
        """Test analyst recommendations extraction"""
        recs = financial_agent._extract_analyst_recommendations(mock_finnhub_data)

        assert isinstance(recs, AnalystRecommendations)
        assert recs.strong_buy == 10
        assert recs.buy == 15
        assert recs.hold == 8
        assert recs.sell == 2
        assert recs.strong_sell == 1
        assert recs.total_analysts == 36
        assert recs.consensus == "Buy"
        assert recs.period == "2024-01"

    def test_extract_analyst_recommendations_error(self, financial_agent):
        """Test analyst recommendations extraction with error"""
        finnhub_data = {"error": "finnhub failed"}

        recs = financial_agent._extract_analyst_recommendations(finnhub_data)

        assert recs is None

    def test_extract_news_sentiment_success(self, financial_agent, mock_finnhub_data):
        """Test news sentiment extraction"""
        sentiment = financial_agent._extract_news_sentiment(mock_finnhub_data)

        assert isinstance(sentiment, NewsSentiment)
        assert sentiment.articles_count == 10
        assert sentiment.sentiment_score == 0.35
        assert sentiment.sentiment == "Positive"
        assert len(sentiment.recent_headlines) == 3

    def test_extract_news_sentiment_error(self, financial_agent):
        """Test news sentiment extraction with error"""
        finnhub_data = {"error": "finnhub failed"}

        sentiment = financial_agent._extract_news_sentiment(finnhub_data)

        assert sentiment is None

    def test_get_data_sources_all_available(self, financial_agent, mock_yfinance_data, mock_finnhub_data, mock_sec_data):
        """Test data source detection when all sources available"""
        sources = financial_agent._get_data_sources(mock_yfinance_data, mock_finnhub_data, mock_sec_data)

        assert "yfinance" in sources
        assert "finnhub" in sources
        assert "sec_edgar" in sources
        assert len(sources) == 3

    def test_get_data_sources_partial_availability(self, financial_agent, mock_yfinance_data):
        """Test data source detection with some sources unavailable"""
        fh_data = {"error": "finnhub failed"}
        sec_data = {"error": "sec failed"}

        sources = financial_agent._get_data_sources(mock_yfinance_data, fh_data, sec_data)

        assert "yfinance" in sources
        assert "finnhub" not in sources
        assert "sec_edgar" not in sources
        assert len(sources) == 1

    def test_format_enhanced_financial_data(self, financial_agent, mock_yfinance_data, mock_finnhub_data, mock_sec_data):
        """Test enhanced financial data formatting for LLM"""
        analyst_recs = AnalystRecommendations(
            strong_buy=10, buy=15, hold=8, sell=2, strong_sell=1,
            total_analysts=36, consensus="Buy", period="2024-01"
        )
        news_sentiment = NewsSentiment(
            articles_count=10, sentiment_score=0.35, sentiment="Positive",
            recent_headlines=["Headline 1", "Headline 2"]
        )
        cross_validation = [
            DataSourceValidation(
                metric="market_cap",
                yfinance_value=800_000_000_000,
                finnhub_value=800_000_000_000,
                discrepancy_pct=0.0,
                is_valid=True
            )
        ]

        formatted = financial_agent._format_enhanced_financial_data(
            mock_yfinance_data, mock_finnhub_data, mock_sec_data,
            analyst_recs, news_sentiment, cross_validation
        )

        assert "yfinance Data" in formatted
        assert "Finnhub Data" in formatted
        assert "Analyst Recommendations" in formatted
        assert "News Sentiment" in formatted
        assert "SEC Filing" in formatted
        assert "Consensus: Buy" in formatted
        assert "Positive" in formatted

    @pytest.mark.asyncio
    async def test_execute_internal_full_integration(self, financial_agent, mock_yfinance_data, mock_finnhub_data, mock_sec_data):
        """Test full execution with all components"""
        with patch('consultantos.agents.financial_agent.yfinance_tool', return_value=mock_yfinance_data), \
             patch('consultantos.agents.financial_agent.finnhub_tool', return_value=mock_finnhub_data), \
             patch('consultantos.agents.financial_agent.sec_edgar_tool', return_value=mock_sec_data):

            # Mock LLM response
            mock_llm_result = FinancialSnapshot(
                ticker="TSLA",
                market_cap=800_000_000_000,
                revenue=96_000_000_000,
                revenue_growth=15.5,
                profit_margin=0.15,
                pe_ratio=65.5,
                key_metrics={"test": "data"},
                risk_assessment="Medium - Growth stock with execution risks"
            )

            with patch.object(financial_agent, 'generate_structured', return_value=mock_llm_result):
                result = await financial_agent._execute_internal({
                    "company": "Tesla",
                    "ticker": "TSLA"
                })

                assert isinstance(result, FinancialSnapshot)
                assert result.ticker == "TSLA"
                assert result.analyst_recommendations is not None
                assert result.analyst_recommendations.consensus == "Buy"
                assert result.news_sentiment is not None
                assert result.news_sentiment.sentiment == "Positive"
                assert "yfinance" in result.data_sources
                assert "finnhub" in result.data_sources
                assert len(result.cross_validation) > 0

    @pytest.mark.asyncio
    async def test_execute_internal_missing_ticker(self, financial_agent):
        """Test execution fails without ticker"""
        with pytest.raises(ValueError, match="Ticker symbol is required"):
            await financial_agent._execute_internal({
                "company": "Tesla"
            })

    @pytest.mark.asyncio
    async def test_execute_internal_fallback_on_llm_failure(self, financial_agent, mock_yfinance_data, mock_finnhub_data, mock_sec_data):
        """Test fallback response when LLM generation fails"""
        with patch('consultantos.agents.financial_agent.yfinance_tool', return_value=mock_yfinance_data), \
             patch('consultantos.agents.financial_agent.finnhub_tool', return_value=mock_finnhub_data), \
             patch('consultantos.agents.financial_agent.sec_edgar_tool', return_value=mock_sec_data):

            # Mock LLM failure
            with patch.object(financial_agent, 'generate_structured', side_effect=Exception("LLM error")):
                result = await financial_agent._execute_internal({
                    "company": "Tesla",
                    "ticker": "TSLA"
                })

                assert isinstance(result, FinancialSnapshot)
                assert result.ticker == "TSLA"
                assert result.market_cap == 800_000_000_000
                assert "Partial data available" in result.risk_assessment

    def test_create_fallback_response(self, financial_agent, mock_yfinance_data, mock_finnhub_data):
        """Test fallback response creation"""
        analyst_recs = AnalystRecommendations(
            strong_buy=10, buy=15, hold=8, sell=2, strong_sell=1,
            total_analysts=36, consensus="Buy"
        )
        news_sentiment = NewsSentiment(
            articles_count=10, sentiment_score=0.35, sentiment="Positive",
            recent_headlines=[]
        )
        cross_validation = []

        result = financial_agent._create_fallback_response(
            "TSLA", mock_yfinance_data, mock_finnhub_data,
            analyst_recs, news_sentiment, ["yfinance", "finnhub"], cross_validation
        )

        assert isinstance(result, FinancialSnapshot)
        assert result.ticker == "TSLA"
        assert result.analyst_recommendations == analyst_recs
        assert result.news_sentiment == news_sentiment
        assert result.data_sources == ["yfinance", "finnhub"]


class TestPerformanceAndEfficiency:
    """Test performance characteristics of enhanced agent"""

    @pytest.mark.asyncio
    async def test_parallel_execution_speed(self, monkeypatch):
        """Test that parallel execution is faster than sequential"""
        import time

        agent = FinancialAgent()

        # Mock slow data sources
        async def slow_fetch(delay):
            await asyncio.sleep(delay)
            return {"data": "test"}

        with patch('consultantos.agents.financial_agent.yfinance_tool', side_effect=lambda x: slow_fetch(0.1)), \
             patch('consultantos.agents.financial_agent.finnhub_tool', side_effect=lambda x: slow_fetch(0.1)), \
             patch('consultantos.agents.financial_agent.sec_edgar_tool', side_effect=lambda x: slow_fetch(0.1)):

            start = time.time()
            await agent._fetch_all_sources("TSLA")
            duration = time.time() - start

            # Parallel execution should take ~0.1s (not 0.3s for sequential)
            assert duration < 0.25, f"Parallel execution took {duration}s, expected < 0.25s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
