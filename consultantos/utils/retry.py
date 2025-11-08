"""
Retry logic with exponential backoff for external API calls
"""
import asyncio
import logging
from typing import TypeVar, Callable, Any, Optional, Tuple
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    exceptions: Tuple[type, ...] = (Exception,)


async def retry_with_backoff(
    func: Callable[..., T],
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,),
    func_name: Optional[str] = None,
    *args,
    **kwargs
) -> T:
    """
    Retry function with exponential backoff
    
    Args:
        func: Function to retry (can be async or sync)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
        exceptions: Tuple of exception types to catch and retry
        func_name: Optional name for logging
        **kwargs: Arguments to pass to func
    
    Returns:
        Result from successful function call
    
    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    func_display_name = func_name or getattr(func, '__name__', 'unknown')
    
    for attempt in range(max_retries):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warning(
                    f"{func_display_name}: Attempt {attempt + 1}/{max_retries} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)
                delay = min(delay * exponential_base, max_delay)
            else:
                logger.error(
                    f"{func_display_name}: All {max_retries} attempts failed. "
                    f"Last error: {e}"
                )
                raise
    
    if last_exception:
        raise last_exception
    raise Exception("Retry failed without exception")


def retry_decorator(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[type, ...] = (Exception,)
):
    """
    Decorator for retrying functions with exponential backoff
    
    Usage:
        @retry_decorator(max_retries=3, initial_delay=1.0)
        async def my_function(arg1, arg2):
            # function implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            return await retry_with_backoff(
                func,
                max_retries=max_retries,
                initial_delay=initial_delay,
                max_delay=max_delay,
                exponential_base=exponential_base,
                exceptions=exceptions,
                func_name=func.__name__,
                *args,
                **kwargs
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            # For sync functions, we need to handle differently
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__}: Attempt {attempt + 1}/{max_retries} failed: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        import time
                        time.sleep(delay)
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        logger.error(f"{func.__name__}: All {max_retries} attempts failed")
                        raise
            
            if last_exception:
                raise last_exception
            raise Exception("Retry failed without exception")
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

