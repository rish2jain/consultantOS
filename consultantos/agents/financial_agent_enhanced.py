"""
Enhanced Financial Agent with multi-source data fetching and cross-validation
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import (
    FinancialSnapshot,
    AnalystRecommendations,
    NewsSentiment,
    DataSourceValidation
)
from consultantos.tools import yfinance_tool, sec_edgar_tool
from consultantos.tools.finnhub_tool import finnhub_tool
from consultantos.utils.schemas import FinancialDataSchema, log_validation_metrics

logger = logging.getLogger(__name__)


class FinancialAgentEnhanced(BaseAgent):
    """
    Enhanced financial analyst agent with multi-source data integration.

    Features:
    - Parallel data fetching from yfinance and Finnhub
    - Cross-validation between data sources
    - Analyst recommendations from Finnhub
    - News sentiment analysis
    - Graceful degradation when sources unavailable
    """

    def __init__(self):
        super().__init__(name="financial_analyst_enhanced")
        self.instruction = """
        You are a financial analyst with expertise in:
        - Financial statement analysis
        - Valuation metrics interpretation
        - Risk assessment
        - Market sentiment analysis
        - Analyst consensus interpretation

        Analyze company financial performance using multiple data sources.
        Cross-validate data between sources and flag discrepancies.
        Focus on: revenue growth, profitability, cash flow, valuation metrics,
        analyst recommendations, and market sentiment.
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> FinancialSnapshot:
        """
        Execute enhanced financial analysis with multi-source data.

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - ticker: Stock ticker symbol (required)

        Returns:
            Enhanced FinancialSnapshot with cross-validated data
        """
        company = input_data.get("company", "")
        ticker = input_data.get("ticker")

        if not ticker:
            raise ValueError(
                f"Ticker symbol is required for company '{company}'. "
                "Please provide a ticker parameter."
            )

        # Fetch data from all sources in parallel
        logger.info(f"Fetching financial data for {ticker} from multiple sources")
        yfinance_data, finnhub_data, sec_data = await self._fetch_all_sources(ticker)

        # Cross-validate data between sources
        cross_validation = self._cross_validate_sources(yfinance_data, finnhub_data)

        # Extract analyst recommendations
        analyst_recs = self._extract_analyst_recommendations(finnhub_data)

        # Extract news sentiment
        news_sentiment = self._extract_news_sentiment(finnhub_data)

        # Determine which sources were used
        data_sources = self._get_data_sources(yfinance_data, finnhub_data, sec_data)

        # Format financial context for LLM
        financial_context = self._format_enhanced_financial_data(
            yfinance_data, finnhub_data, sec_data, analyst_recs, news_sentiment, cross_validation
        )

        # Generate structured analysis
        prompt = f"""
        {self.instruction}

        Analyze financials for: {company} (Ticker: {ticker})

        Financial Data (Multi-Source):
        {financial_context}

        Data Sources: {', '.join(data_sources)}

        Extract and structure:
        1. Ticker symbol
        2. Market cap (cross-validated value)
        3. Revenue (latest annual)
        4. Revenue growth (YoY %)
        5. Profit margin
        6. P/E ratio
        7. Key metrics (dict)
        8. Risk assessment (Low/Medium/High with rationale, considering analyst consensus and sentiment)

        Note any significant discrepancies between data sources in your analysis.
        """

        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=FinancialSnapshot
            )

            # Enhance with Finnhub data
            result.analyst_recommendations = analyst_recs
            result.news_sentiment = news_sentiment
            result.data_sources = data_sources
            result.cross_validation = cross_validation

            # Validate the result
            result_dict = result.model_dump()
            is_valid, error_msg, cleaned_data = FinancialDataSchema.validate_financial_snapshot(result_dict)

            log_validation_metrics("financial_enhanced", is_valid, error_msg)

            if not is_valid:
                logger.warning(
                    f"Enhanced financial data validation failed for {ticker}: {error_msg}. "
                    "Returning cleaned partial data."
                )

            return FinancialSnapshot(**cleaned_data)

        except Exception as e:
            logger.error(f"Enhanced financial analysis failed for {ticker}: {e}", exc_info=True)
            # Fallback to basic analysis
            return self._create_fallback_response(
                ticker, yfinance_data, finnhub_data, analyst_recs, news_sentiment,
                data_sources, cross_validation
            )

    async def _fetch_all_sources(self, ticker: str) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Fetch data from all sources in parallel.

        Returns:
            Tuple of (yfinance_data, finnhub_data, sec_data)
        """
        async def fetch_yfinance():
            """Async wrapper for yfinance"""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, yfinance_tool, ticker)

        async def fetch_finnhub():
            """Async wrapper for Finnhub"""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, finnhub_tool, ticker)

        async def fetch_sec():
            """Async wrapper for SEC"""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, sec_edgar_tool, ticker)

        # Execute all fetches in parallel
        results = await asyncio.gather(
            fetch_yfinance(),
            fetch_finnhub(),
            fetch_sec(),
            return_exceptions=True
        )

        # Unpack results with error handling
        yfinance_data = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        finnhub_data = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        sec_data = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}

        return yfinance_data, finnhub_data, sec_data or {}

    def _cross_validate_sources(
        self,
        yfinance_data: Dict[str, Any],
        finnhub_data: Dict[str, Any],
        threshold: float = 0.20  # 20% discrepancy threshold
    ) -> List[DataSourceValidation]:
        """
        Cross-validate data between yfinance and Finnhub.

        Args:
            yfinance_data: Data from yfinance
            finnhub_data: Data from Finnhub
            threshold: Maximum acceptable discrepancy percentage (default: 20%)

        Returns:
            List of validation results
        """
        validations = []

        # Skip if either source has errors
        if yfinance_data.get("error") or finnhub_data.get("error"):
            return validations

        # Extract values for comparison
        yf_info = yfinance_data.get("company_info", {})
        fh_profile = finnhub_data.get("profile", {})

        # Market cap validation
        yf_market_cap = yf_info.get("marketCap")
        fh_market_cap = fh_profile.get("market_cap")

        if yf_market_cap and fh_market_cap:
            # Finnhub returns market cap in millions, yfinance in actual value
            fh_market_cap_actual = fh_market_cap * 1_000_000
            discrepancy_pct = abs(yf_market_cap - fh_market_cap_actual) / yf_market_cap * 100

            is_valid = discrepancy_pct <= threshold * 100
            note = None if is_valid else f"Discrepancy exceeds {threshold*100}% threshold"

            validations.append(DataSourceValidation(
                metric="market_cap",
                yfinance_value=yf_market_cap,
                finnhub_value=fh_market_cap_actual,
                discrepancy_pct=round(discrepancy_pct, 2),
                is_valid=is_valid,
                note=note
            ))

        return validations

    def _extract_analyst_recommendations(
        self,
        finnhub_data: Dict[str, Any]
    ) -> Optional[AnalystRecommendations]:
        """Extract analyst recommendations from Finnhub data"""
        if finnhub_data.get("error"):
            return None

        recs = finnhub_data.get("recommendations", {})
        if recs.get("error"):
            return None

        return AnalystRecommendations(
            strong_buy=recs.get("strong_buy", 0),
            buy=recs.get("buy", 0),
            hold=recs.get("hold", 0),
            sell=recs.get("sell", 0),
            strong_sell=recs.get("strong_sell", 0),
            total_analysts=recs.get("total_analysts", 0),
            consensus=recs.get("consensus", "Unknown"),
            period=recs.get("period")
        )

    def _extract_news_sentiment(
        self,
        finnhub_data: Dict[str, Any]
    ) -> Optional[NewsSentiment]:
        """Extract news sentiment from Finnhub data"""
        if finnhub_data.get("error"):
            return None

        news = finnhub_data.get("news", {})
        if news.get("error"):
            return None

        # Extract headlines
        headlines = []
        for article in news.get("articles", [])[:5]:  # Top 5 headlines
            if article.get("headline"):
                headlines.append(article["headline"])

        return NewsSentiment(
            articles_count=news.get("articles_count", 0),
            sentiment_score=news.get("sentiment_score", 0.0),
            sentiment=news.get("sentiment", "Neutral"),
            recent_headlines=headlines
        )

    def _get_data_sources(
        self,
        yfinance_data: Dict[str, Any],
        finnhub_data: Dict[str, Any],
        sec_data: Dict[str, Any]
    ) -> List[str]:
        """Determine which data sources were successfully used"""
        sources = []
        if not yfinance_data.get("error"):
            sources.append("yfinance")
        if not finnhub_data.get("error"):
            sources.append("finnhub")
        if sec_data and not sec_data.get("error"):
            sources.append("sec_edgar")
        return sources

    def _format_enhanced_financial_data(
        self,
        yfinance_data: Dict[str, Any],
        finnhub_data: Dict[str, Any],
        sec_data: Dict[str, Any],
        analyst_recs: Optional[AnalystRecommendations],
        news_sentiment: Optional[NewsSentiment],
        cross_validation: List[DataSourceValidation]
    ) -> str:
        """Format enhanced financial data for LLM"""
        lines = []

        # yfinance data
        if not yfinance_data.get("error"):
            info = yfinance_data.get("company_info", {})
            lines.append("=== yfinance Data ===")
            lines.append(f"Market Cap: ${info.get('marketCap', 'N/A'):,}" if isinstance(info.get('marketCap'), (int, float)) else f"Market Cap: {info.get('marketCap', 'N/A')}")
            lines.append(f"Revenue: ${info.get('totalRevenue', 'N/A'):,}" if isinstance(info.get('totalRevenue'), (int, float)) else f"Revenue: {info.get('totalRevenue', 'N/A')}")
            lines.append(f"Profit Margin: {info.get('profitMargins', 'N/A')}")
            lines.append(f"P/E Ratio: {info.get('trailingPE', 'N/A')}")

        # Finnhub data
        if not finnhub_data.get("error"):
            profile = finnhub_data.get("profile", {})
            lines.append("\n=== Finnhub Data ===")
            lines.append(f"Company: {profile.get('name', 'N/A')}")
            lines.append(f"Industry: {profile.get('industry', 'N/A')}")
            lines.append(f"Market Cap (millions): ${profile.get('market_cap', 'N/A')}")

        # Analyst recommendations
        if analyst_recs:
            lines.append("\n=== Analyst Recommendations ===")
            lines.append(f"Consensus: {analyst_recs.consensus}")
            lines.append(f"Total Analysts: {analyst_recs.total_analysts}")
            lines.append(f"Strong Buy: {analyst_recs.strong_buy}, Buy: {analyst_recs.buy}")
            lines.append(f"Hold: {analyst_recs.hold}")
            lines.append(f"Sell: {analyst_recs.sell}, Strong Sell: {analyst_recs.strong_sell}")

        # News sentiment
        if news_sentiment:
            lines.append("\n=== News Sentiment ===")
            lines.append(f"Sentiment: {news_sentiment.sentiment} (score: {news_sentiment.sentiment_score:.2f})")
            lines.append(f"Articles Analyzed: {news_sentiment.articles_count}")
            if news_sentiment.recent_headlines:
                lines.append("Recent Headlines:")
                for headline in news_sentiment.recent_headlines[:3]:
                    lines.append(f"  - {headline}")

        # Cross-validation warnings
        if cross_validation:
            lines.append("\n=== Data Validation ===")
            for validation in cross_validation:
                if not validation.is_valid:
                    lines.append(f"⚠️  {validation.metric}: {validation.discrepancy_pct}% discrepancy ({validation.note})")

        # SEC data
        if sec_data and not sec_data.get("error"):
            lines.append(f"\n=== SEC Filing ===")
            lines.append(f"Filing Date: {sec_data.get('filing_date', 'N/A')}")

        return "\n".join(lines)

    def _create_fallback_response(
        self,
        ticker: str,
        yfinance_data: Dict[str, Any],
        finnhub_data: Dict[str, Any],
        analyst_recs: Optional[AnalystRecommendations],
        news_sentiment: Optional[NewsSentiment],
        data_sources: List[str],
        cross_validation: List[DataSourceValidation]
    ) -> FinancialSnapshot:
        """Create fallback response when LLM generation fails"""
        info = yfinance_data.get("company_info", {}) if not yfinance_data.get("error") else {}

        fallback_data = {
            "ticker": ticker,
            "market_cap": info.get("marketCap"),
            "revenue": info.get("totalRevenue"),
            "revenue_growth": None,
            "profit_margin": info.get("profitMargins"),
            "pe_ratio": info.get("trailingPE"),
            "key_metrics": info,
            "risk_assessment": "Medium - Partial data available from automated sources",
            "analyst_recommendations": analyst_recs,
            "news_sentiment": news_sentiment,
            "data_sources": data_sources,
            "cross_validation": cross_validation
        }

        # Validate fallback
        is_valid, error_msg, cleaned_fallback = FinancialDataSchema.validate_financial_snapshot(fallback_data)
        log_validation_metrics("financial_enhanced_fallback", is_valid, error_msg)

        return FinancialSnapshot(**cleaned_fallback)
