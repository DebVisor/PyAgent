"""Resilience patterns for component_23_6."""

from typing import Callable, Any, Optional
from functools import wraps
import time

def retry(max_attempts: int = 3, backoff: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = backoff ** attempt
                    time.sleep(wait)
        return wrapper
    return decorator

class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, threshold: int = 5, timeout: int = 60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker."""
        if self.failures >= self.threshold:
            if time.time() - self.last_failure < self.timeout:
                raise Exception("Circuit breaker open")
            self.failures = 0
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            raise

@retry(max_attempts=3, backoff=2.0)
def resilient_call():
    """Example resilient function."""
    return "success"
