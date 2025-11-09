"""
Financial data tools for financial analyst agent
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import yfinance as yf
from consultantos.utils.circuit_breaker import CircuitBreaker, CircuitState

# Import metrics from monitoring module (not package)
# For hackathon demo, make metrics optional to avoid import issues
try:
    from consultantos import monitoring as monitoring_module
    metrics = monitoring_module.metrics
except (ImportError, AttributeError):
    metrics = None

# Optional import for SEC EDGAR
try:
    from edgar import Company
    EDGAR_AVAILABLE = True
except ImportError:
    EDGAR_AVAILABLE = False
    Company = None

# Circuit breakers for financial APIs
_yfinance_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    name="yfinance_api"
)

_sec_circuit_breaker = CircuitBreaker(
    failure_threshold=3,
    recovery_timeout=120,
    name="sec_edgar_api"
)


def _yfinance_internal(ticker: str) -> Dict[str, Any]:
    """Internal yfinance function"""
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Historical data
    history = stock.history(period="1y")
    
    # Financial statements
    financials = stock.financials
    
    return {
        "company_info": info,
        "price_history": history.to_dict() if not history.empty else {},
        "financials": financials.to_dict() if financials is not None and not financials.empty else {},
        "ticker": ticker
    }


def yfinance_tool(ticker: str) -> Dict[str, Any]:
    """
    Get stock and financial data using yfinance with retry and circuit breaker
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with company info, price history, and financials
    """
    def _fetch_with_retry():
        """Sync retry wrapper"""
        max_retries = 3
        delay = 1.0
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return _yfinance_internal(ticker)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"yfinance attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
                    time.sleep(delay)
                    delay = min(delay * 2.0, 10.0)
                else:
                    raise
        
        if last_exception:
            raise last_exception
    
    start_time = time.time()
    try:
        # Use circuit breaker's synchronous API
        response = _yfinance_circuit_breaker.call_sync(_fetch_with_retry)
        duration = time.time() - start_time
        
        # Track metrics
        if metrics:
            metrics.track_api_call("yfinance", success=True, duration=duration)
            metrics.track_circuit_breaker_state("yfinance_api", "closed")
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        
        # Track metrics
        if metrics:
            metrics.track_api_call("yfinance", success=False, duration=duration)
            metrics.track_circuit_breaker_state("yfinance_api", _yfinance_circuit_breaker.state.value)
        
        logger.error(f"yfinance tool failed: {e}", exc_info=True)
        return {
            "error": f"Failed to fetch financial data: {str(e)}",
            "ticker": ticker,
            "company_info": {},
            "price_history": {},
            "financials": {}
        }


def _sec_edgar_internal(ticker: str) -> Optional[Dict[str, Any]]:
    """Internal SEC EDGAR function"""
    if not EDGAR_AVAILABLE or Company is None:
        return {
            "error": "SEC EDGAR tools not available. Install edgartools package.",
            "ticker": ticker
        }
    
    company = Company(ticker)
    filings = company.get_filings(form="10-K", count=1)
    
    if filings and len(filings) > 0:
        latest = filings[0]
        return {
            "filing_date": str(latest.filing_date) if hasattr(latest, 'filing_date') else None,
            "filing_type": "10-K",
            "ticker": ticker
        }
    return None


def sec_edgar_tool(ticker: str) -> Optional[Dict[str, Any]]:
    """
    Get SEC filings data using edgartools with retry and circuit breaker
    
    Args:
        ticker: Stock ticker symbol
    
    Returns:
        Dictionary with filing information or None if not found
    """
    def _fetch_with_retry():
        """Sync retry wrapper"""
        max_retries = 2
        delay = 2.0
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return _sec_edgar_internal(ticker)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"SEC EDGAR attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
                    time.sleep(delay)
                    delay = min(delay * 2.0, 15.0)
                else:
                    raise
        
        if last_exception:
            raise last_exception
    
    try:
        # Check circuit breaker
        if _sec_circuit_breaker.state == CircuitState.OPEN:
            if not _sec_circuit_breaker._should_attempt_recovery():
                return {"error": "SEC EDGAR circuit breaker is OPEN", "ticker": ticker}
            _sec_circuit_breaker.state = CircuitState.HALF_OPEN
        
        try:
            response = _fetch_with_retry()
            # Success
            if _sec_circuit_breaker.state == CircuitState.HALF_OPEN:
                _sec_circuit_breaker.success_count += 1
                if _sec_circuit_breaker.success_count >= 2:
                    _sec_circuit_breaker.state = CircuitState.CLOSED
            _sec_circuit_breaker.failure_count = 0
            return response
        except Exception as e:
            # Failure
            _sec_circuit_breaker.failure_count += 1
            _sec_circuit_breaker.last_failure_time = datetime.now()
            if _sec_circuit_breaker.failure_count >= _sec_circuit_breaker.failure_threshold:
                _sec_circuit_breaker.state = CircuitState.OPEN
            raise
    except Exception as e:
        logger.warning(f"SEC EDGAR tool failed: {e}")
        return {
            "error": f"Failed to fetch SEC filings: {str(e)}",
            "ticker": ticker
        }