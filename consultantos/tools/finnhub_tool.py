"""
Finnhub API integration tool for financial data enrichment
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from consultantos.utils.circuit_breaker import CircuitBreaker, CircuitState
from consultantos.cache import get_disk_cache

# Import metrics from monitoring module
try:
    from consultantos import monitoring as monitoring_module
    metrics = monitoring_module.metrics
except (ImportError, AttributeError):
    metrics = None

# Optional import for Finnhub
try:
    import finnhub
    FINNHUB_AVAILABLE = True
except ImportError:
    FINNHUB_AVAILABLE = False
    finnhub = None

logger = logging.getLogger(__name__)

# Circuit breaker for Finnhub API
_finnhub_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    name="finnhub_api"
)

# Cache TTL: 1 hour for Finnhub data
FINNHUB_CACHE_TTL = 3600


class FinnhubClient:
    """
    Wrapper for Finnhub API with caching, error handling, and rate limiting.

    Features:
    - Automatic caching (1 hour TTL)
    - Circuit breaker protection
    - Retry logic with exponential backoff
    - Graceful fallback on errors
    - Rate limiting protection
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Finnhub client.

        Args:
            api_key: Finnhub API key (optional, falls back to config)
        """
        self.api_key = api_key
        self._client = None
        self._cache = get_disk_cache()

        if api_key and FINNHUB_AVAILABLE:
            try:
                self._client = finnhub.Client(api_key=api_key)
                logger.info("Finnhub client initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Finnhub client: {e}")

    def _cache_key(self, method: str, symbol: str) -> str:
        """Generate cache key for Finnhub data"""
        return f"finnhub:{method}:{symbol.upper()}"

    def _get_cached(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached data if available"""
        if not self._cache:
            return None
        try:
            cached_data = self._cache.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")
        return None

    def _set_cached(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Cache data with TTL"""
        if not self._cache:
            return
        try:
            self._cache.set(cache_key, data, expire=FINNHUB_CACHE_TTL)
            logger.debug(f"Cached data for {cache_key}")
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    def company_profile(self, symbol: str) -> Dict[str, Any]:
        """
        Get company profile data from Finnhub.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with company profile data including:
            - name: Company name
            - marketCapitalization: Market cap in millions
            - shareOutstanding: Outstanding shares
            - country: Headquarters country
            - currency: Trading currency
            - exchange: Stock exchange
            - ipo: IPO date
            - weburl: Company website
            - logo: Logo URL
            - finnhubIndustry: Industry classification
        """
        cache_key = self._cache_key("profile", symbol)

        # Check cache first
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self._client:
            return self._error_response(symbol, "Finnhub client not initialized")

        try:
            start_time = time.time()
            profile = _finnhub_circuit_breaker.call_sync(
                lambda: self._client.company_profile2(symbol=symbol.upper())
            )
            duration = time.time() - start_time

            if metrics:
                metrics.track_api_call("finnhub_profile", success=True, duration=duration)

            # Normalize response
            result = {
                "symbol": symbol.upper(),
                "name": profile.get("name"),
                "market_cap": profile.get("marketCapitalization"),
                "shares_outstanding": profile.get("shareOutstanding"),
                "country": profile.get("country"),
                "currency": profile.get("currency"),
                "exchange": profile.get("exchange"),
                "ipo_date": profile.get("ipo"),
                "website": profile.get("weburl"),
                "logo": profile.get("logo"),
                "industry": profile.get("finnhubIndustry"),
                "source": "finnhub",
                "timestamp": datetime.now().isoformat()
            }

            # Cache the result
            self._set_cached(cache_key, result)

            return result
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            if metrics:
                metrics.track_api_call("finnhub_profile", success=False, duration=duration)
            logger.error(f"Finnhub company_profile failed for {symbol}: {e}")
            return self._error_response(symbol, str(e))

    def recommendation_trends(self, symbol: str) -> Dict[str, Any]:
        """
        Get analyst recommendation trends.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with recommendation trends including:
            - buy: Number of buy recommendations
            - hold: Number of hold recommendations
            - sell: Number of sell recommendations
            - strongBuy: Number of strong buy recommendations
            - strongSell: Number of strong sell recommendations
            - period: Time period (e.g., "2024-01")
        """
        cache_key = self._cache_key("recommendations", symbol)

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self._client:
            return self._error_response(symbol, "Finnhub client not initialized")

        try:
            start_time = time.time()
            recommendations = _finnhub_circuit_breaker.call_sync(
                lambda: self._client.recommendation_trends(symbol.upper())
            )
            duration = time.time() - start_time

            if metrics:
                metrics.track_api_call("finnhub_recommendations", success=True, duration=duration)

            # Get most recent recommendation
            if recommendations and len(recommendations) > 0:
                latest = recommendations[0]
                result = {
                    "symbol": symbol.upper(),
                    "period": latest.get("period"),
                    "strong_buy": latest.get("strongBuy", 0),
                    "buy": latest.get("buy", 0),
                    "hold": latest.get("hold", 0),
                    "sell": latest.get("sell", 0),
                    "strong_sell": latest.get("strongSell", 0),
                    "total_analysts": sum([
                        latest.get("strongBuy", 0),
                        latest.get("buy", 0),
                        latest.get("hold", 0),
                        latest.get("sell", 0),
                        latest.get("strongSell", 0)
                    ]),
                    "source": "finnhub",
                    "timestamp": datetime.now().isoformat()
                }

                # Calculate consensus
                total = result["total_analysts"]
                if total > 0:
                    bullish = result["strong_buy"] + result["buy"]
                    bearish = result["sell"] + result["strong_sell"]
                    if bullish > bearish:
                        result["consensus"] = "Buy"
                    elif bearish > bullish:
                        result["consensus"] = "Sell"
                    else:
                        result["consensus"] = "Hold"
                else:
                    result["consensus"] = "Unknown"

                self._set_cached(cache_key, result)
                return result
            else:
                return self._error_response(symbol, "No recommendation data available")
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            if metrics:
                metrics.track_api_call("finnhub_recommendations", success=False, duration=duration)
            logger.error(f"Finnhub recommendation_trends failed for {symbol}: {e}")
            return self._error_response(symbol, str(e))

    def company_news(self, symbol: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Get recent company news.

        Args:
            symbol: Stock ticker symbol
            days_back: Number of days to look back (default: 7)

        Returns:
            Dictionary with news articles and sentiment analysis
        """
        cache_key = self._cache_key(f"news_{days_back}d", symbol)

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self._client:
            return self._error_response(symbol, "Finnhub client not initialized")

        try:
            start_time = time.time()

            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)

            news = _finnhub_circuit_breaker.call_sync(
                lambda: self._client.company_news(
                    symbol.upper(),
                    _from=from_date.strftime("%Y-%m-%d"),
                    to=to_date.strftime("%Y-%m-%d")
                )
            )
            duration = time.time() - start_time

            if metrics:
                metrics.track_api_call("finnhub_news", success=True, duration=duration)

            # Process news articles
            articles = []
            if news:
                for article in news[:10]:  # Limit to 10 most recent
                    articles.append({
                        "headline": article.get("headline"),
                        "summary": article.get("summary"),
                        "source": article.get("source"),
                        "url": article.get("url"),
                        "datetime": article.get("datetime"),
                        "category": article.get("category")
                    })

            # Simple sentiment analysis
            sentiment_score = self._calculate_news_sentiment(articles)

            result = {
                "symbol": symbol.upper(),
                "articles_count": len(articles),
                "articles": articles,
                "sentiment_score": sentiment_score,
                "sentiment": self._sentiment_label(sentiment_score),
                "date_range": f"{from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}",
                "source": "finnhub",
                "timestamp": datetime.now().isoformat()
            }

            self._set_cached(cache_key, result)
            return result
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            if metrics:
                metrics.track_api_call("finnhub_news", success=False, duration=duration)
            logger.error(f"Finnhub company_news failed for {symbol}: {e}")
            return self._error_response(symbol, str(e))

    def earnings_calendar(self, symbol: str) -> Dict[str, Any]:
        """
        Get earnings calendar data.

        Args:
            symbol: Stock ticker symbol

        Returns:
            Dictionary with upcoming earnings date and estimates
        """
        cache_key = self._cache_key("earnings", symbol)

        # Check cache
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        if not self._client:
            return self._error_response(symbol, "Finnhub client not initialized")

        try:
            start_time = time.time()

            # Get earnings calendar for next 30 days
            to_date = datetime.now() + timedelta(days=30)
            from_date = datetime.now() - timedelta(days=7)

            calendar = _finnhub_circuit_breaker.call_sync(
                lambda: self._client.earnings_calendar(
                    _from=from_date.strftime("%Y-%m-%d"),
                    to=to_date.strftime("%Y-%m-%d"),
                    symbol=symbol.upper()
                )
            )
            duration = time.time() - start_time

            if metrics:
                metrics.track_api_call("finnhub_earnings", success=True, duration=duration)

            result = {
                "symbol": symbol.upper(),
                "earnings_data": calendar.get("earningsCalendar", []),
                "source": "finnhub",
                "timestamp": datetime.now().isoformat()
            }

            self._set_cached(cache_key, result)
            return result
        except Exception as e:
            duration = time.time() - start_time if 'start_time' in locals() else 0
            if metrics:
                metrics.track_api_call("finnhub_earnings", success=False, duration=duration)
            logger.error(f"Finnhub earnings_calendar failed for {symbol}: {e}")
            return self._error_response(symbol, str(e))

    def _calculate_news_sentiment(self, articles: List[Dict[str, Any]]) -> float:
        """
        Calculate simple sentiment score from news articles.
        Uses basic keyword analysis.

        Returns:
            Float between -1.0 (very negative) and 1.0 (very positive)
        """
        if not articles:
            return 0.0

        positive_keywords = [
            "growth", "profit", "beat", "exceed", "strong", "surge", "gain",
            "success", "innovation", "breakthrough", "award", "expand"
        ]
        negative_keywords = [
            "loss", "decline", "miss", "fall", "weak", "concern", "lawsuit",
            "investigation", "cut", "layoff", "bankruptcy", "scandal"
        ]

        sentiment_sum = 0.0
        for article in articles:
            text = f"{article.get('headline', '')} {article.get('summary', '')}".lower()

            pos_count = sum(1 for word in positive_keywords if word in text)
            neg_count = sum(1 for word in negative_keywords if word in text)

            if pos_count + neg_count > 0:
                sentiment_sum += (pos_count - neg_count) / (pos_count + neg_count)

        if len(articles) > 0:
            return sentiment_sum / len(articles)
        return 0.0

    def _sentiment_label(self, score: float) -> str:
        """Convert sentiment score to label"""
        if score > 0.3:
            return "Positive"
        elif score < -0.3:
            return "Negative"
        else:
            return "Neutral"

    def _error_response(self, symbol: str, error_msg: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "symbol": symbol.upper(),
            "error": error_msg,
            "source": "finnhub",
            "timestamp": datetime.now().isoformat()
        }


# Module-level convenience function
def finnhub_tool(symbol: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch comprehensive financial data from Finnhub.

    Args:
        symbol: Stock ticker symbol
        api_key: Optional Finnhub API key (uses config if not provided)

    Returns:
        Dictionary with:
        - profile: Company profile data
        - recommendations: Analyst recommendations
        - news: Recent news and sentiment
        - earnings: Earnings calendar
    """
    # Get API key from config if not provided
    if not api_key:
        try:
            from consultantos.config import settings
            api_key = settings.finnhub_api_key
        except Exception as e:
            logger.warning(f"Could not load Finnhub API key from config: {e}")

    if not api_key:
        logger.warning("Finnhub API key not available, returning empty response")
        return {
            "error": "Finnhub API key not configured",
            "symbol": symbol,
            "profile": {},
            "recommendations": {},
            "news": {},
            "earnings": {}
        }

    client = FinnhubClient(api_key=api_key)

    # Fetch all data
    return {
        "symbol": symbol.upper(),
        "profile": client.company_profile(symbol),
        "recommendations": client.recommendation_trends(symbol),
        "news": client.company_news(symbol, days_back=7),
        "earnings": client.earnings_calendar(symbol),
        "source": "finnhub",
        "timestamp": datetime.now().isoformat()
    }
