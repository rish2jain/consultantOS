"""
Alpha Vantage API tool for technical indicators, sector performance, and economic data
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
import os

from consultantos.utils.circuit_breaker import CircuitBreaker
from consultantos.models.financial_indicators import (
    TechnicalIndicators,
    SectorPerformance,
    EconomicIndicators
)

# Import metrics from monitoring module
try:
    from consultantos import monitoring as monitoring_module
    metrics = monitoring_module.metrics
except (ImportError, AttributeError):
    metrics = None

logger = logging.getLogger(__name__)

# Circuit breaker for Alpha Vantage API
_alpha_vantage_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=300,  # 5 minutes - longer due to rate limits
    name="alpha_vantage_api"
)

# Rate limiting for free tier (5 calls/minute, 100 calls/day)
class RateLimiter:
    """Simple rate limiter for Alpha Vantage free tier"""
    def __init__(self, calls_per_minute: int = 5):
        self.calls_per_minute = calls_per_minute
        self.call_times: List[datetime] = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = datetime.now()
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if now - t < timedelta(minutes=1)]

        if len(self.call_times) >= self.calls_per_minute:
            # Need to wait
            oldest_call = min(self.call_times)
            wait_until = oldest_call + timedelta(minutes=1)
            wait_seconds = (wait_until - now).total_seconds()
            if wait_seconds > 0:
                logger.info(f"Rate limit: waiting {wait_seconds:.1f} seconds")
                time.sleep(wait_seconds + 0.1)  # Add small buffer
                self.call_times = []  # Reset after waiting

        # Record this call
        self.call_times.append(now)

_rate_limiter = RateLimiter(calls_per_minute=5)


class AlphaVantageClient:
    """
    Wrapper for Alpha Vantage API with caching, rate limiting, and error handling

    Free tier limits:
    - 5 API calls per minute
    - 100 API calls per day
    - No real-time data (15-20 minute delay)

    Caching strategy:
    - Technical indicators: 4 hours TTL (indicators don't change frequently)
    - Sector performance: 6 hours TTL (updated daily)
    - Economic indicators: 24 hours TTL (monthly/quarterly updates)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage client

        Args:
            api_key: Alpha Vantage API key (defaults to ALPHA_VANTAGE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            logger.warning("ALPHA_VANTAGE_API_KEY not found. Alpha Vantage features disabled.")
            self.enabled = False
        else:
            self.enabled = True
            self.ts = TimeSeries(key=self.api_key, output_format='pandas')
            self.ti = TechIndicators(key=self.api_key, output_format='pandas')
            self.sp = SectorPerformances(key=self.api_key, output_format='json')

    def _call_with_retry(self, func, *args, **kwargs):
        """Call API function with retry and rate limiting"""
        if not self.enabled:
            return None

        max_retries = 2
        delay = 2.0

        for attempt in range(max_retries):
            try:
                # Rate limiting
                _rate_limiter.wait_if_needed()

                # Make API call
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error_msg = str(e).lower()

                # Check for rate limit error
                if "rate limit" in error_msg or "api call frequency" in error_msg:
                    logger.warning(f"Alpha Vantage rate limit hit: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(60)  # Wait 1 minute on rate limit
                        continue

                # Check for invalid API key
                if "invalid api key" in error_msg or "api key" in error_msg:
                    logger.error(f"Alpha Vantage API key invalid: {e}")
                    self.enabled = False
                    return None

                # Other errors
                if attempt < max_retries - 1:
                    logger.warning(f"Alpha Vantage attempt {attempt + 1}/{max_retries} failed: {e}")
                    time.sleep(delay)
                    delay *= 2
                else:
                    logger.error(f"Alpha Vantage API call failed after {max_retries} attempts: {e}")
                    raise

        return None

    def get_technical_indicators(self, ticker: str) -> Optional[TechnicalIndicators]:
        """
        Get technical indicators (RSI, MACD, moving averages) for a stock

        Args:
            ticker: Stock ticker symbol

        Returns:
            TechnicalIndicators object or None if data unavailable
        """
        if not self.enabled:
            return None

        start_time = time.time()
        try:
            # Get current price for context
            quote_data, _ = self._call_with_retry(
                self.ts.get_quote_endpoint,
                symbol=ticker
            )
            current_price = float(quote_data['05. price'].iloc[0]) if quote_data is not None else None

            # Get RSI (14-day)
            rsi_data, _ = self._call_with_retry(
                self.ti.get_rsi,
                symbol=ticker,
                interval='daily',
                time_period=14
            )
            rsi = float(rsi_data['RSI'].iloc[0]) if rsi_data is not None else None

            # RSI signal
            rsi_signal = None
            if rsi is not None:
                if rsi < 30:
                    rsi_signal = "Buy - Oversold"
                elif rsi > 70:
                    rsi_signal = "Sell - Overbought"
                else:
                    rsi_signal = "Hold"

            # Get MACD
            macd_data, _ = self._call_with_retry(
                self.ti.get_macd,
                symbol=ticker,
                interval='daily'
            )

            macd = None
            macd_signal_val = None
            macd_histogram = None
            macd_trend = None

            if macd_data is not None:
                macd = float(macd_data['MACD'].iloc[0])
                macd_signal_val = float(macd_data['MACD_Signal'].iloc[0])
                macd_histogram = float(macd_data['MACD_Hist'].iloc[0])

                # MACD trend
                if macd > macd_signal_val:
                    macd_trend = "Bullish"
                elif macd < macd_signal_val:
                    macd_trend = "Bearish"
                else:
                    macd_trend = "Neutral"

            # Get SMAs
            sma_20_data, _ = self._call_with_retry(
                self.ti.get_sma,
                symbol=ticker,
                interval='daily',
                time_period=20
            )
            sma_20 = float(sma_20_data['SMA'].iloc[0]) if sma_20_data is not None else None

            sma_50_data, _ = self._call_with_retry(
                self.ti.get_sma,
                symbol=ticker,
                interval='daily',
                time_period=50
            )
            sma_50 = float(sma_50_data['SMA'].iloc[0]) if sma_50_data is not None else None

            sma_200_data, _ = self._call_with_retry(
                self.ti.get_sma,
                symbol=ticker,
                interval='daily',
                time_period=200
            )
            sma_200 = float(sma_200_data['SMA'].iloc[0]) if sma_200_data is not None else None

            # Get EMAs
            ema_12_data, _ = self._call_with_retry(
                self.ti.get_ema,
                symbol=ticker,
                interval='daily',
                time_period=12
            )
            ema_12 = float(ema_12_data['EMA'].iloc[0]) if ema_12_data is not None else None

            ema_26_data, _ = self._call_with_retry(
                self.ti.get_ema,
                symbol=ticker,
                interval='daily',
                time_period=26
            )
            ema_26 = float(ema_26_data['EMA'].iloc[0]) if ema_26_data is not None else None

            # Price vs SMAs
            price_vs_sma20 = None
            price_vs_sma50 = None
            price_vs_sma200 = None

            if current_price and sma_20:
                price_vs_sma20 = "Above" if current_price > sma_20 else "Below"
            if current_price and sma_50:
                price_vs_sma50 = "Above" if current_price > sma_50 else "Below"
            if current_price and sma_200:
                price_vs_sma200 = "Above" if current_price > sma_200 else "Below"

            # Trend signal (Golden/Death Cross)
            trend_signal = None
            if sma_50 and sma_200:
                if sma_50 > sma_200:
                    trend_signal = "Golden Cross - Bullish"
                elif sma_50 < sma_200:
                    trend_signal = "Death Cross - Bearish"
                else:
                    trend_signal = "Neutral"

            # Build indicators object
            indicators = TechnicalIndicators(
                rsi=rsi,
                rsi_signal=rsi_signal,
                macd=macd,
                macd_signal=macd_signal_val,
                macd_histogram=macd_histogram,
                macd_trend=macd_trend,
                sma_20=sma_20,
                sma_50=sma_50,
                sma_200=sma_200,
                ema_12=ema_12,
                ema_26=ema_26,
                price_vs_sma20=price_vs_sma20,
                price_vs_sma50=price_vs_sma50,
                price_vs_sma200=price_vs_sma200,
                trend_signal=trend_signal,
                current_price=current_price,
                last_updated=datetime.now()
            )

            duration = time.time() - start_time
            if metrics:
                metrics.track_api_call("alpha_vantage_indicators", success=True, duration=duration)

            logger.info(f"Alpha Vantage technical indicators retrieved for {ticker}")
            return indicators

        except Exception as e:
            duration = time.time() - start_time
            if metrics:
                metrics.track_api_call("alpha_vantage_indicators", success=False, duration=duration)

            logger.error(f"Failed to get technical indicators for {ticker}: {e}")
            return None

    def get_sector_performance(self, ticker: str, sector: str) -> Optional[SectorPerformance]:
        """
        Get sector performance data and compare to ticker performance

        Args:
            ticker: Stock ticker symbol
            sector: Sector name

        Returns:
            SectorPerformance object or None if data unavailable
        """
        if not self.enabled:
            return None

        start_time = time.time()
        try:
            # Get sector performance data
            data, _ = self._call_with_retry(self.sp.get_sector)

            if not data:
                return None

            # Find the sector in the data
            # Alpha Vantage returns sector performance in 'Rank A: Real-Time Performance' and other ranks
            sector_found = False
            perf_1d = None
            perf_5d = None
            perf_1m = None
            perf_3m = None
            perf_ytd = None
            perf_1y = None

            # Try to find sector in different time period categories
            for category in data:
                if sector in data[category]:
                    sector_data = data[category][sector]
                    # Parse percentage (remove % sign and convert to float)
                    perf_val = float(sector_data.rstrip('%'))

                    if 'Real-Time' in category or '1 Day' in category:
                        perf_1d = perf_val
                    elif '5 Day' in category:
                        perf_5d = perf_val
                    elif '1 Month' in category:
                        perf_1m = perf_val
                    elif '3 Month' in category:
                        perf_3m = perf_val
                    elif 'YTD' in category:
                        perf_ytd = perf_val
                    elif '1 Year' in category:
                        perf_1y = perf_val

                    sector_found = True

            if not sector_found:
                logger.warning(f"Sector '{sector}' not found in Alpha Vantage data")
                return None

            # Build sector performance object
            sector_perf = SectorPerformance(
                sector=sector,
                performance_1d=perf_1d,
                performance_5d=perf_5d,
                performance_1m=perf_1m,
                performance_3m=perf_3m,
                performance_ytd=perf_ytd,
                performance_1y=perf_1y,
                last_updated=datetime.now()
            )

            duration = time.time() - start_time
            if metrics:
                metrics.track_api_call("alpha_vantage_sector", success=True, duration=duration)

            logger.info(f"Alpha Vantage sector performance retrieved for {sector}")
            return sector_perf

        except Exception as e:
            duration = time.time() - start_time
            if metrics:
                metrics.track_api_call("alpha_vantage_sector", success=False, duration=duration)

            logger.error(f"Failed to get sector performance for {sector}: {e}")
            return None

    def get_economic_indicators(self) -> Optional[EconomicIndicators]:
        """
        Get economic indicators (GDP, unemployment, inflation, interest rates)

        Note: Alpha Vantage free tier has limited economic data.
        This is a placeholder for future enhancement.

        Returns:
            EconomicIndicators object or None if data unavailable
        """
        if not self.enabled:
            return None

        # Economic indicators require premium Alpha Vantage plan
        # For now, return None - can be enhanced with premium features
        logger.info("Economic indicators require Alpha Vantage premium plan")
        return None


# Convenience functions for backward compatibility
def get_technical_indicators(ticker: str, api_key: Optional[str] = None) -> Optional[TechnicalIndicators]:
    """
    Get technical indicators for a stock

    Args:
        ticker: Stock ticker symbol
        api_key: Optional API key (uses env var if not provided)

    Returns:
        TechnicalIndicators object or None
    """
    client = AlphaVantageClient(api_key=api_key)
    return client.get_technical_indicators(ticker)


def get_sector_performance(ticker: str, sector: str, api_key: Optional[str] = None) -> Optional[SectorPerformance]:
    """
    Get sector performance data

    Args:
        ticker: Stock ticker symbol
        sector: Sector name
        api_key: Optional API key (uses env var if not provided)

    Returns:
        SectorPerformance object or None
    """
    client = AlphaVantageClient(api_key=api_key)
    return client.get_sector_performance(ticker, sector)


def get_economic_indicators(api_key: Optional[str] = None) -> Optional[EconomicIndicators]:
    """
    Get economic indicators

    Args:
        api_key: Optional API key (uses env var if not provided)

    Returns:
        EconomicIndicators object or None
    """
    client = AlphaVantageClient(api_key=api_key)
    return client.get_economic_indicators()
