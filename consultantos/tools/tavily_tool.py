"""
Tavily web search tool for research agent
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from tavily import TavilyClient
from consultantos.config import settings
from consultantos.utils.circuit_breaker import CircuitBreaker, CircuitState

# Import metrics from monitoring module (not package)
# For hackathon demo, make metrics optional to avoid import issues
try:
    from consultantos import monitoring as monitoring_module
    metrics = monitoring_module.metrics
except (ImportError, AttributeError):
    metrics = None

logger = logging.getLogger(__name__)

# Lazy initialization of Tavily client
_tavily_client: Optional[TavilyClient] = None

# Circuit breaker for Tavily API
_tavily_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60,
    name="tavily_api"
)


def _get_tavily_client() -> TavilyClient:
    """Get or create Tavily client instance"""
    global _tavily_client
    if _tavily_client is None:
        api_key = settings.tavily_api_key or os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not found. Please set it as an environment variable.")
        _tavily_client = TavilyClient(api_key=api_key)
    return _tavily_client


def _tavily_search_internal(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Internal Tavily search function"""
    client = _get_tavily_client()
    response = client.search(
        query=query,
        max_results=max_results,
        search_depth="advanced"
    )
    
    # Format response for agent consumption
    return {
        "results": response.get("results", []),
        "query": query,
        "total_results": len(response.get("results", []))
    }


def tavily_search_tool(query: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Execute Tavily web search with retry and circuit breaker
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return
    
    Returns:
        Dictionary with search results including sources and content
    """
    def _search_with_retry():
        """Sync wrapper for retry logic"""
        import time
        max_retries = 3
        delay = 1.0
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return _tavily_search_internal(query, max_results)
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    logger.warning(f"Tavily search attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
                    delay = min(delay * 2.0, 10.0)
                else:
                    logger.error(f"Tavily search failed after {max_retries} attempts")
                    raise
        
        if last_exception:
            raise last_exception
    
    try:
        # Check circuit breaker state (sync check)
        if _tavily_circuit_breaker.state == CircuitState.OPEN:
            if not _tavily_circuit_breaker._should_attempt_recovery():
                raise Exception(f"Circuit breaker is OPEN for tavily_api. Service unavailable.")
            _tavily_circuit_breaker.state = CircuitState.HALF_OPEN
        
        # Execute with retry
        import time
        start_time = time.time()
        try:
            response = _search_with_retry()
            duration = time.time() - start_time

            # Track metrics (optional)
            if metrics:
                metrics.track_api_call("tavily", success=True, duration=duration)
                metrics.track_circuit_breaker_state("tavily_api", "closed")
            
            # Success - reset circuit breaker
            if _tavily_circuit_breaker.state == CircuitState.HALF_OPEN:
                _tavily_circuit_breaker.success_count += 1
                if _tavily_circuit_breaker.success_count >= 2:
                    _tavily_circuit_breaker.state = CircuitState.CLOSED
                    _tavily_circuit_breaker.failure_count = 0
            _tavily_circuit_breaker.failure_count = 0
            return response
        except Exception as e:
            duration = time.time() - start_time

            # Track metrics (optional)
            if metrics:
                metrics.track_api_call("tavily", success=False, duration=duration)
                metrics.track_circuit_breaker_state("tavily_api", _tavily_circuit_breaker.state.value)
            
            # Failure - update circuit breaker
            _tavily_circuit_breaker.failure_count += 1
            _tavily_circuit_breaker.last_failure_time = datetime.now()
            if _tavily_circuit_breaker.failure_count >= _tavily_circuit_breaker.failure_threshold:
                _tavily_circuit_breaker.state = CircuitState.OPEN
            raise
    except Exception as e:
        logger.error(f"Tavily search failed: {e}", exc_info=True)
        return {
            "error": f"Search failed: {str(e)}",
            "results": [],
            "query": query,
            "total_results": 0
        }

