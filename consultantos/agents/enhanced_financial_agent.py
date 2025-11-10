"""
Enhanced Financial Agent - Multi-source financial analysis with technical indicators
Combines yfinance, Finnhub, and Alpha Vantage for comprehensive financial intelligence
"""
import asyncio
from typing import Dict, Any, List, Optional
from consultantos.agents.base_agent import BaseAgent
from consultantos.models import FinancialSnapshot
from consultantos.tools import yfinance_tool, sec_edgar_tool
from consultantos.utils.schemas import FinancialDataSchema, log_validation_metrics

# Finnhub integration (if available)
try:
    from consultantos.tools.finnhub_tool import get_finnhub_data, FINNHUB_AVAILABLE
except ImportError:
    FINNHUB_AVAILABLE = False
    get_finnhub_data = None

# Alpha Vantage integration
try:
    from consultantos.tools.alpha_vantage_tool import (
        get_technical_indicators,
        get_sector_performance,
        AlphaVantageClient
    )
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    get_technical_indicators = None
    get_sector_performance = None


class EnhancedFinancialAgent(BaseAgent):
    """
    Enhanced Financial Agent with multi-source data fusion

    Data Sources:
    1. yfinance: Core financial metrics, price data
    2. Finnhub: Analyst recommendations, news sentiment
    3. Alpha Vantage: Technical indicators, sector performance

    Features:
    - Parallel data fetching for performance
    - Graceful degradation (works without Finnhub/Alpha Vantage)
    - Data source validation and confidence scoring
    - Smart data fusion across sources
    """

    def __init__(self):
        super().__init__(name="enhanced_financial_analyst")
        self.instruction = """
        You are a financial analyst with expertise in:
        - Financial statement analysis
        - Valuation metrics interpretation
        - Technical analysis and trading signals
        - Sector analysis and competitive positioning
        - Risk assessment with multi-source validation

        Analyze company financial performance using multiple data sources.
        Focus on: fundamentals, technical indicators, sector context, sentiment.
        """

    async def _execute_internal(self, input_data: Dict[str, Any]) -> FinancialSnapshot:
        """
        Execute enhanced financial analysis using multi-source data

        Process:
        1. Parallel fetch from all available sources
        2. Validate and cross-check data
        3. Calculate confidence scores
        4. Synthesize into comprehensive snapshot

        Args:
            input_data: Dictionary containing:
                - company: Company name
                - ticker: Stock ticker symbol (required)
                - sector: Company sector (optional, for sector analysis)

        Returns:
            FinancialSnapshot with multi-source data and confidence scores
        """
        company = input_data.get("company", "")
        ticker = input_data.get("ticker")
        sector = input_data.get("sector")

        # Require ticker
        if not ticker:
            raise ValueError(
                f"Ticker symbol is required for company '{company}'. "
                "Please provide a ticker parameter."
            )

        # Phase 1: Parallel data fetching from all sources
        fetch_tasks = {
            "yfinance": self._fetch_yfinance_data(ticker),
            "sec": self._fetch_sec_data(ticker),
        }

        if FINNHUB_AVAILABLE and get_finnhub_data:
            fetch_tasks["finnhub"] = self._fetch_finnhub_data(ticker)

        if ALPHA_VANTAGE_AVAILABLE and get_technical_indicators:
            fetch_tasks["alpha_vantage"] = self._fetch_alpha_vantage_data(ticker, sector)

        # Await all fetches in parallel
        results = {}
        for source, task in fetch_tasks.items():
            try:
                results[source] = await task
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to fetch {source} data for {ticker}: {e}")
                results[source] = None

        # Phase 2: Data fusion and validation
        financial_data = self._fuse_data_sources(
            ticker=ticker,
            company=company,
            sector=sector,
            yfinance_data=results.get("yfinance"),
            sec_data=results.get("sec"),
            finnhub_data=results.get("finnhub"),
            alpha_vantage_data=results.get("alpha_vantage"),
        )

        # Phase 3: LLM analysis with structured output
        prompt = self._build_analysis_prompt(
            company=company,
            ticker=ticker,
            financial_data=financial_data
        )

        try:
            result = await self.generate_structured(
                prompt=prompt,
                response_model=FinancialSnapshot
            )

            # Validate result
            result_dict = result.model_dump()
            is_valid, error_msg, cleaned_data = FinancialDataSchema.validate_financial_snapshot(result_dict)
            log_validation_metrics("enhanced_financial", is_valid, error_msg)

            if not is_valid:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Financial data validation failed for {ticker}: {error_msg}. "
                    "Returning cleaned partial data."
                )

            return FinancialSnapshot(**cleaned_data)

        except Exception as e:
            # Fallback to basic data
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM analysis failed for {ticker}: {e}. Using fallback data.")
            return self._create_fallback_snapshot(ticker, financial_data)

    async def _fetch_yfinance_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch data from yfinance (synchronous tool, wrapped in async)"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, yfinance_tool, ticker)

    async def _fetch_sec_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch data from SEC EDGAR"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, sec_edgar_tool, ticker)

    async def _fetch_finnhub_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch data from Finnhub"""
        if not FINNHUB_AVAILABLE or not get_finnhub_data:
            return None
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_finnhub_data, ticker)

    async def _fetch_alpha_vantage_data(self, ticker: str, sector: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fetch technical indicators and sector performance from Alpha Vantage"""
        if not ALPHA_VANTAGE_AVAILABLE:
            return None

        loop = asyncio.get_event_loop()

        # Fetch technical indicators
        indicators = await loop.run_in_executor(None, get_technical_indicators, ticker)

        # Fetch sector performance (if sector provided)
        sector_perf = None
        if sector and get_sector_performance:
            sector_perf = await loop.run_in_executor(None, get_sector_performance, ticker, sector)

        return {
            "technical_indicators": indicators,
            "sector_performance": sector_perf,
        }

    def _fuse_data_sources(
        self,
        ticker: str,
        company: str,
        sector: Optional[str],
        yfinance_data: Optional[Dict[str, Any]],
        sec_data: Optional[Dict[str, Any]],
        finnhub_data: Optional[Dict[str, Any]],
        alpha_vantage_data: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Fuse data from multiple sources with validation

        Returns:
            Comprehensive financial data dict with confidence scores
        """
        fused = {
            "ticker": ticker,
            "company": company,
            "sector": sector,
            "sources_available": [],
            "data_confidence": 0.0,
        }

        # yfinance data (primary source)
        if yfinance_data and not yfinance_data.get("error"):
            fused["sources_available"].append("yfinance")
            info = yfinance_data.get("company_info", {})
            fused["market_cap"] = info.get("marketCap")
            fused["revenue"] = info.get("totalRevenue")
            fused["profit_margin"] = info.get("profitMargins")
            fused["pe_ratio"] = info.get("trailingPE")
            fused["key_metrics"] = info
            fused["data_confidence"] = 0.7  # Base confidence with yfinance

        # SEC data (adds regulatory context)
        if sec_data and not sec_data.get("error"):
            fused["sources_available"].append("sec")
            fused["data_confidence"] = min(fused.get("data_confidence", 0) + 0.1, 1.0)

        # Finnhub data (adds analyst sentiment)
        if finnhub_data:
            fused["sources_available"].append("finnhub")
            fused["analyst_recommendations"] = finnhub_data.get("recommendations")
            fused["news_sentiment"] = finnhub_data.get("sentiment")
            fused["data_confidence"] = min(fused.get("data_confidence", 0) + 0.1, 1.0)

        # Alpha Vantage data (adds technical analysis)
        if alpha_vantage_data:
            indicators = alpha_vantage_data.get("technical_indicators")
            sector_perf = alpha_vantage_data.get("sector_performance")

            if indicators:
                fused["sources_available"].append("alpha_vantage")
                fused["rsi"] = indicators.rsi
                fused["rsi_signal"] = indicators.rsi_signal
                fused["macd_trend"] = indicators.macd_trend
                fused["trend_signal"] = indicators.trend_signal
                fused["price_vs_sma50"] = indicators.price_vs_sma50
                fused["price_vs_sma200"] = indicators.price_vs_sma200
                fused["current_price"] = indicators.current_price
                fused["data_confidence"] = min(fused.get("data_confidence", 0) + 0.1, 1.0)

            if sector_perf:
                fused["sector_performance_ytd"] = sector_perf.performance_ytd
                fused["company_vs_sector"] = sector_perf.company_vs_sector_ytd

        return fused

    def _build_analysis_prompt(
        self,
        company: str,
        ticker: str,
        financial_data: Dict[str, Any]
    ) -> str:
        """Build comprehensive analysis prompt with multi-source data"""
        sources = ", ".join(financial_data.get("sources_available", ["yfinance"]))

        prompt = f"""
        {self.instruction}

        Analyze financials for: {company} (Ticker: {ticker})

        **Data Sources**: {sources}
        **Confidence**: {financial_data.get('data_confidence', 0.7):.0%}

        **Fundamental Metrics**:
        - Market Cap: {self._format_number(financial_data.get('market_cap'))}
        - Revenue: {self._format_number(financial_data.get('revenue'))}
        - Profit Margin: {self._format_percent(financial_data.get('profit_margin'))}
        - P/E Ratio: {financial_data.get('pe_ratio', 'N/A')}
        """

        # Add technical analysis if available
        if "alpha_vantage" in financial_data.get("sources_available", []):
            prompt += f"""

        **Technical Analysis** (Alpha Vantage):
        - RSI: {financial_data.get('rsi', 'N/A')} ({financial_data.get('rsi_signal', 'N/A')})
        - MACD Trend: {financial_data.get('macd_trend', 'N/A')}
        - Trend Signal: {financial_data.get('trend_signal', 'N/A')}
        - Price vs 50-day SMA: {financial_data.get('price_vs_sma50', 'N/A')}
        - Price vs 200-day SMA: {financial_data.get('price_vs_sma200', 'N/A')}
        - Current Price: ${financial_data.get('current_price', 'N/A')}
        """

        # Add sector analysis if available
        if financial_data.get("sector_performance_ytd"):
            prompt += f"""

        **Sector Analysis**:
        - Sector: {financial_data.get('sector', 'N/A')}
        - Sector YTD Performance: {self._format_percent(financial_data.get('sector_performance_ytd'))}
        - Company vs Sector: {financial_data.get('company_vs_sector', 'N/A')}
        """

        prompt += """

        Extract and structure:
        1. Core financial metrics
        2. Technical indicators (if available)
        3. Sector context (if available)
        4. Risk assessment (integrate technical + fundamental analysis)
        5. Data sources used
        6. Overall confidence score
        """

        return prompt

    def _format_number(self, value: Optional[float]) -> str:
        """Format large numbers for display"""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"${value:,.0f}"
        return str(value)

    def _format_percent(self, value: Optional[float]) -> str:
        """Format percentage for display"""
        if value is None:
            return "N/A"
        if isinstance(value, (int, float)):
            return f"{value * 100:.1f}%" if value < 1 else f"{value:.1f}%"
        return str(value)

    def _create_fallback_snapshot(
        self,
        ticker: str,
        financial_data: Dict[str, Any]
    ) -> FinancialSnapshot:
        """Create fallback snapshot when LLM analysis fails"""
        fallback = {
            "ticker": ticker,
            "market_cap": financial_data.get("market_cap"),
            "revenue": financial_data.get("revenue"),
            "revenue_growth": None,
            "profit_margin": financial_data.get("profit_margin"),
            "pe_ratio": financial_data.get("pe_ratio"),
            "key_metrics": financial_data.get("key_metrics", {}),
            "risk_assessment": "Medium - Limited analysis available",
            "data_sources": financial_data.get("sources_available", ["yfinance"]),
        }

        # Add technical indicators if available
        if "rsi" in financial_data:
            fallback.update({
                "rsi": financial_data.get("rsi"),
                "rsi_signal": financial_data.get("rsi_signal"),
                "macd_trend": financial_data.get("macd_trend"),
                "trend_signal": financial_data.get("trend_signal"),
                "price_vs_sma50": financial_data.get("price_vs_sma50"),
                "price_vs_sma200": financial_data.get("price_vs_sma200"),
                "current_price": financial_data.get("current_price"),
            })

        # Add sector analysis if available
        if financial_data.get("sector"):
            fallback.update({
                "sector": financial_data.get("sector"),
                "sector_performance_ytd": financial_data.get("sector_performance_ytd"),
                "company_vs_sector": financial_data.get("company_vs_sector"),
            })

        # Validate fallback
        is_valid, error_msg, cleaned_fallback = FinancialDataSchema.validate_financial_snapshot(fallback)
        log_validation_metrics("enhanced_financial_fallback", is_valid, error_msg)

        return FinancialSnapshot(**cleaned_fallback)
