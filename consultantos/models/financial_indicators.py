"""
Financial Indicators Models for Alpha Vantage Integration
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class TechnicalIndicators(BaseModel):
    """Technical indicator data from Alpha Vantage"""

    # Relative Strength Index
    rsi: Optional[float] = Field(None, ge=0, le=100, description="RSI value (0-100), <30=oversold, >70=overbought")
    rsi_signal: Optional[str] = Field(None, description="Buy/Sell/Hold signal from RSI")

    # Moving Average Convergence Divergence
    macd: Optional[float] = Field(None, description="MACD line value")
    macd_signal: Optional[float] = Field(None, description="MACD signal line")
    macd_histogram: Optional[float] = Field(None, description="MACD histogram (MACD - Signal)")
    macd_trend: Optional[str] = Field(None, description="Bullish/Bearish/Neutral")

    # Moving Averages
    sma_20: Optional[float] = Field(None, description="20-day Simple Moving Average")
    sma_50: Optional[float] = Field(None, description="50-day Simple Moving Average")
    sma_200: Optional[float] = Field(None, description="200-day Simple Moving Average")
    ema_12: Optional[float] = Field(None, description="12-day Exponential Moving Average")
    ema_26: Optional[float] = Field(None, description="26-day Exponential Moving Average")

    # Price vs Moving Averages
    price_vs_sma20: Optional[str] = Field(None, description="Above/Below 20-day SMA")
    price_vs_sma50: Optional[str] = Field(None, description="Above/Below 50-day SMA")
    price_vs_sma200: Optional[str] = Field(None, description="Above/Below 200-day SMA")

    # Golden Cross / Death Cross
    trend_signal: Optional[str] = Field(
        None,
        description="Golden Cross (bullish) / Death Cross (bearish) / Neutral"
    )

    # Additional indicators
    stochastic_k: Optional[float] = Field(None, ge=0, le=100, description="Stochastic %K")
    stochastic_d: Optional[float] = Field(None, ge=0, le=100, description="Stochastic %D")
    adx: Optional[float] = Field(None, ge=0, le=100, description="Average Directional Index (trend strength)")

    # Metadata
    last_updated: Optional[datetime] = Field(None, description="When indicators were last calculated")
    current_price: Optional[float] = Field(None, description="Current stock price")

    class Config:
        json_schema_extra = {
            "example": {
                "rsi": 42.5,
                "rsi_signal": "Hold",
                "macd": 1.25,
                "macd_signal": 0.85,
                "macd_histogram": 0.40,
                "macd_trend": "Bullish",
                "sma_20": 150.25,
                "sma_50": 148.75,
                "sma_200": 145.50,
                "price_vs_sma20": "Above",
                "price_vs_sma200": "Above",
                "trend_signal": "Golden Cross",
                "current_price": 152.30
            }
        }


class SectorPerformance(BaseModel):
    """Sector performance data from Alpha Vantage"""

    sector: str = Field(..., description="Sector name (e.g., 'Information Technology')")

    # Performance metrics across different time periods
    performance_1d: Optional[float] = Field(None, description="1-day performance (%)")
    performance_5d: Optional[float] = Field(None, description="5-day performance (%)")
    performance_1m: Optional[float] = Field(None, description="1-month performance (%)")
    performance_3m: Optional[float] = Field(None, description="3-month performance (%)")
    performance_ytd: Optional[float] = Field(None, description="Year-to-date performance (%)")
    performance_1y: Optional[float] = Field(None, description="1-year performance (%)")

    # Rankings
    rank_1d: Optional[int] = Field(None, ge=1, le=11, description="Rank among 11 sectors (1=best)")
    rank_ytd: Optional[int] = Field(None, ge=1, le=11, description="YTD rank among sectors")

    # Relative to company
    company_vs_sector_1m: Optional[str] = Field(None, description="Outperforming/Underperforming/Inline")
    company_vs_sector_ytd: Optional[str] = Field(None, description="Outperforming/Underperforming/Inline")

    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "sector": "Information Technology",
                "performance_1d": 0.45,
                "performance_5d": 2.1,
                "performance_1m": 5.3,
                "performance_3m": 12.8,
                "performance_ytd": 24.5,
                "performance_1y": 32.7,
                "rank_1d": 3,
                "rank_ytd": 2,
                "company_vs_sector_1m": "Outperforming",
                "company_vs_sector_ytd": "Inline"
            }
        }


class EconomicIndicators(BaseModel):
    """Economic indicators from Alpha Vantage"""

    # GDP
    gdp_current: Optional[float] = Field(None, description="Current GDP (billions)")
    gdp_growth_rate: Optional[float] = Field(None, description="GDP growth rate (%)")
    gdp_quarter: Optional[str] = Field(None, description="Quarter (e.g., '2024-Q3')")

    # Unemployment
    unemployment_rate: Optional[float] = Field(None, ge=0, le=100, description="Unemployment rate (%)")
    unemployment_month: Optional[str] = Field(None, description="Month (e.g., '2024-10')")

    # Inflation
    cpi: Optional[float] = Field(None, description="Consumer Price Index")
    inflation_rate: Optional[float] = Field(None, description="Inflation rate (% YoY)")
    inflation_month: Optional[str] = Field(None, description="Month (e.g., '2024-10')")

    # Interest Rates
    federal_funds_rate: Optional[float] = Field(None, description="Federal Funds Rate (%)")
    treasury_yield_10y: Optional[float] = Field(None, description="10-Year Treasury Yield (%)")

    # Sentiment
    economic_sentiment: Optional[str] = Field(
        None,
        description="Positive/Neutral/Negative based on indicators"
    )

    # Metadata
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    data_freshness: Optional[str] = Field(None, description="Current/Slightly Stale/Stale")

    class Config:
        json_schema_extra = {
            "example": {
                "gdp_current": 27360.0,
                "gdp_growth_rate": 2.8,
                "gdp_quarter": "2024-Q3",
                "unemployment_rate": 3.8,
                "unemployment_month": "2024-10",
                "cpi": 315.2,
                "inflation_rate": 3.2,
                "inflation_month": "2024-10",
                "federal_funds_rate": 5.33,
                "treasury_yield_10y": 4.25,
                "economic_sentiment": "Positive"
            }
        }


class ComprehensiveFinancialData(BaseModel):
    """Aggregated financial data from multiple sources"""

    # Core identification
    ticker: str
    company_name: str

    # Data from different sources
    technical_indicators: Optional[TechnicalIndicators] = None
    sector_performance: Optional[SectorPerformance] = None
    economic_indicators: Optional[EconomicIndicators] = None

    # Data quality metadata
    sources_available: List[str] = Field(
        default_factory=list,
        description="List of data sources that provided data (yfinance, alpha_vantage, finnhub, etc.)"
    )
    data_confidence: float = Field(
        default=1.0,
        ge=0,
        le=1.0,
        description="Confidence score based on source agreement and data quality"
    )
    missing_data_points: List[str] = Field(
        default_factory=list,
        description="List of data points that could not be retrieved"
    )

    # Analysis timestamp
    analysis_timestamp: datetime = Field(default_factory=datetime.now)

    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "sources_available": ["yfinance", "alpha_vantage", "finnhub"],
                "data_confidence": 0.95,
                "missing_data_points": [],
                "analysis_timestamp": "2024-11-09T10:30:00Z"
            }
        }
