"""
Google Trends tool for market analyst agent
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, List
from pytrends.request import TrendReq
import pandas as pd
from consultantos.utils.circuit_breaker import CircuitBreaker, CircuitState
from consultantos.monitoring import metrics

logger = logging.getLogger(__name__)

# Initialize Google Trends client
pytrend = TrendReq(hl='en-US', tz=360)

# Circuit breaker for Google Trends API
_trends_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=120,  # Longer timeout (rate limits are strict)
    name="google_trends_api"
)


def _google_trends_internal(keywords: List[str], timeframe: str = 'today 12-m') -> Dict[str, Any]:
    """Internal Google Trends function"""
    # Build payload
    pytrend.build_payload(keywords, timeframe=timeframe)
    
    # Interest over time
    interest_data = pytrend.interest_over_time()
    
    # Regional interest
    regional = pytrend.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
    
    # Related queries
    related = pytrend.related_queries()
    
    # Determine trend direction
    trend_direction = "Stable"
    if not interest_data.empty and len(interest_data) > 3:
        recent_avg = interest_data[keywords[0]][-3:].mean()
        earlier_avg = interest_data[keywords[0]][:3].mean()
        
        if recent_avg > earlier_avg * 1.2:
            trend_direction = "Growing"
        elif recent_avg < earlier_avg * 0.8:
            trend_direction = "Declining"
    
    return {
        "search_interest_trend": trend_direction,
        "interest_data": interest_data.to_dict() if not interest_data.empty else {},
        "geographic_distribution": regional.to_dict() if not regional.empty else {},
        "related_queries": related,
        "keywords_analyzed": keywords
    }


def google_trends_tool(keywords: List[str], timeframe: str = 'today 12-m') -> Dict[str, Any]:
    """
    Analyze market trends using Google Trends with retry and circuit breaker
    
    Args:
        keywords: List of keywords to analyze
        timeframe: Time period for analysis (default: last 12 months)
    
    Returns:
        Dictionary with trend data including interest over time, regional data, and related queries
    """
    def _fetch_with_retry():
        """Sync retry wrapper"""
        max_retries = 2
        delay = 2.0
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return _google_trends_internal(keywords, timeframe)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Google Trends attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
                    time.sleep(delay)
                    delay = min(delay * 2.0, 15.0)
                else:
                    raise
        
        if last_exception:
            raise last_exception
    
    try:
        # Check circuit breaker
        if _trends_circuit_breaker.state == CircuitState.OPEN:
            if not _trends_circuit_breaker._should_attempt_recovery():
                raise Exception("Google Trends circuit breaker is OPEN")
            _trends_circuit_breaker.state = CircuitState.HALF_OPEN
        
        start_time = time.time()
        try:
            response = _fetch_with_retry()
            duration = time.time() - start_time
            
            # Track metrics
            metrics.track_api_call("google_trends", success=True, duration=duration)
            metrics.track_circuit_breaker_state("google_trends_api", "closed")
            
            # Success
            if _trends_circuit_breaker.state == CircuitState.HALF_OPEN:
                _trends_circuit_breaker.success_count += 1
                if _trends_circuit_breaker.success_count >= 2:
                    _trends_circuit_breaker.state = CircuitState.CLOSED
            _trends_circuit_breaker.failure_count = 0
            return response
        except Exception as e:
            duration = time.time() - start_time
            
            # Track metrics
            metrics.track_api_call("google_trends", success=False, duration=duration)
            metrics.track_circuit_breaker_state("google_trends_api", _trends_circuit_breaker.state.value)
            
            # Failure
            _trends_circuit_breaker.failure_count += 1
            _trends_circuit_breaker.last_failure_time = datetime.now()
            if _trends_circuit_breaker.failure_count >= _trends_circuit_breaker.failure_threshold:
                _trends_circuit_breaker.state = CircuitState.OPEN
            raise
    except Exception as e:
        logger.error(f"Google Trends tool failed: {e}", exc_info=True)
        return {
            "error": f"Failed to fetch trends data: {str(e)}",
            "search_interest_trend": "Unknown",
            "interest_data": {},
            "geographic_distribution": {},
            "related_queries": {},
            "keywords_analyzed": keywords
        }

