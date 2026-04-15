"""Retry handler with exponential backoff."""

import time
import logging
from typing import Callable, Any, Tuple
import random

logger = logging.getLogger(__name__)


class RetryHandler:
    """Automatic retry logic with exponential backoff and jitter."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def exponential_backoff(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        if attempt == 0:
            return 0.0
        
        # Exponential: 2^attempt
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        
        # Add jitter (±20%)
        jitter = delay * (0.8 + random.random() * 0.4)
        
        return jitter
    
    def retry(self, 
             func: Callable,
             *args,
             **kwargs) -> Tuple[bool, Any, str]:
        """Execute function with retries. Returns (success, result, error_msg)."""
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries + 1}")
                result = func(*args, **kwargs)
                logger.info(f"Success on attempt {attempt + 1}")
                return True, result, None
            
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                
                if attempt < self.max_retries:
                    delay = self.exponential_backoff(attempt)
                    logger.info(f"Waiting {delay:.1f}s before retry...")
                    time.sleep(delay)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded")
        
        return False, None, last_error
    
    def retry_async(self, 
                   func: Callable,
                   *args,
                   **kwargs):
        """Async version of retry. (Placeholder for future async implementation)."""
        # For now, just use sync version
        return self.retry(func, *args, **kwargs)
