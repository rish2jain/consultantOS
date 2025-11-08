"""
Circuit breaker pattern for external API calls
"""
from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import asyncio
import logging
import threading

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures
    
    When failures exceed threshold, circuit opens and rejects requests.
    After recovery timeout, circuit moves to half-open to test recovery.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        name: Optional[str] = None
    ):
        """
        Initialize circuit breaker
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            expected_exception: Exception type to catch
            name: Optional name for logging
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED
        self.name = name or "circuit_breaker"
        self.success_count = 0  # Track successes in half-open state
        self._lock = asyncio.Lock()  # Lock for async thread-safe state access
        self._sync_lock = threading.Lock()  # Lock for sync thread-safe state access
    
    def reset(self):
        """Reset circuit breaker to closed state (thread-safe)"""
        with self._sync_lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
        logger.info(f"{self.name}: Circuit breaker reset to CLOSED")
    
    def _should_attempt_recovery(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        return datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout)
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection (async)
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result from function
        
        Raises:
            Exception if circuit is open or function fails
        """
        # Check circuit state (with lock)
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    logger.info(f"{self.name}: Attempting recovery, moving to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception(
                        f"Circuit breaker is OPEN for {self.name}. "
                        f"Service unavailable. Retry after {self.recovery_timeout}s"
                    )
        
        # Execute function (without holding lock)
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Success handling (with lock)
            async with self._lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    # If we get a few successes, close the circuit
                    if self.success_count >= 2:
                        logger.info(f"{self.name}: Recovery successful, closing circuit")
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        self.success_count = 0
                
                # Reset failure count on success in closed state
                if self.state == CircuitState.CLOSED:
                    self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            # Failure handling (with lock)
            async with self._lock:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                if self.state == CircuitState.HALF_OPEN:
                    # Failure in half-open means service still down
                    logger.warning(f"{self.name}: Recovery failed, reopening circuit")
                    self.state = CircuitState.OPEN
                    self.success_count = 0
                
                if self.failure_count >= self.failure_threshold:
                    if self.state != CircuitState.OPEN:
                        logger.error(
                            f"{self.name}: Failure threshold ({self.failure_threshold}) exceeded, "
                            f"opening circuit"
                        )
                    self.state = CircuitState.OPEN
            
            raise
    
    def call_sync(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute synchronous function with circuit breaker protection
        
        Args:
            func: Synchronous function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
        
        Returns:
            Result from function
        
        Raises:
            Exception if circuit is open or function fails
        """
        
        # Check circuit state (with lock)
        with self._sync_lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_recovery():
                    logger.info(f"{self.name}: Attempting recovery, moving to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise Exception(
                        f"Circuit breaker is OPEN for {self.name}. "
                        f"Service unavailable. Retry after {self.recovery_timeout}s"
                    )
        
        # Execute function (without holding lock)
        try:
            result = func(*args, **kwargs)
            
            # Success handling (with lock)
            with self._sync_lock:
                if self.state == CircuitState.HALF_OPEN:
                    self.success_count += 1
                    if self.success_count >= 2:
                        logger.info(f"{self.name}: Recovery successful, closing circuit")
                        self.state = CircuitState.CLOSED
                        self.failure_count = 0
                        self.success_count = 0
                
                if self.state == CircuitState.CLOSED:
                    self.failure_count = 0
            
            return result
            
        except self.expected_exception as e:
            # Failure handling (with lock)
            with self._sync_lock:
                self.failure_count += 1
                self.last_failure_time = datetime.now()
                
                if self.state == CircuitState.HALF_OPEN:
                    logger.warning(f"{self.name}: Recovery failed, reopening circuit")
                    self.state = CircuitState.OPEN
                    self.success_count = 0
                
                if self.failure_count >= self.failure_threshold:
                    if self.state != CircuitState.OPEN:
                        logger.error(
                            f"{self.name}: Failure threshold ({self.failure_threshold}) exceeded, "
                            f"opening circuit"
                        )
                    self.state = CircuitState.OPEN
            
            raise
    
    def get_state(self) -> CircuitState:
        """Get current circuit state (thread-safe snapshot)"""
        with self._sync_lock:
            return self.state
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics (thread-safe snapshot)"""
        # Create snapshot while holding lock
        with self._sync_lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "success_count": self.success_count,
            }

