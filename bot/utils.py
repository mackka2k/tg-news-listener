"""
Shared utilities and constants
"""

import asyncio
import functools
import logging
from typing import Any, Callable, TypeVar, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants
MAX_CAPTION_LENGTH = 1000
MAX_MESSAGES_TO_FETCH = 100
SAFETY_MULTIPLIER = 5
DEFAULT_RETRY_DELAY = 5
MAX_RETRIES = 3

T = TypeVar('T')


def retry_on_error(
    max_retries: int = MAX_RETRIES,
    delay: int = DEFAULT_RETRY_DELAY,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator to retry async functions on error with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}. "
                            f"Retrying in {wait_time}s..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries} retries failed for {func.__name__}")
            
            raise last_exception
        
        return wrapper
    return decorator


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to max length, preserving word boundaries
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    # Try to truncate at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # Only use word boundary if not too short
        truncated = truncated[:last_space]
    
    return truncated + suffix


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime for logging
    
    Args:
        dt: Datetime to format (defaults to now)
    
    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def sanitize_channel_name(channel: str) -> str:
    """
    Sanitize channel name for logging/display
    
    Args:
        channel: Channel username or ID
    
    Returns:
        Sanitized channel name
    """
    if isinstance(channel, int):
        return f"ID:{channel}"
    
    # Remove @ prefix if present
    return channel.lstrip('@')


def validate_channel_format(channel: str) -> bool:
    """
    Validate channel username format
    
    Args:
        channel: Channel username
    
    Returns:
        True if valid format
    """
    if not channel:
        return False
    
    # Remove @ if present
    clean = channel.lstrip('@')
    
    # Must be alphanumeric + underscores, 5-32 chars
    if not clean.replace('_', '').isalnum():
        return False
    
    return 5 <= len(clean) <= 32


class CircularBuffer:
    """
    Simple circular buffer for storing recent items
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.items = []
    
    def add(self, item: Any) -> None:
        """Add item to buffer"""
        self.items.append(item)
        if len(self.items) > self.max_size:
            self.items.pop(0)
    
    def contains(self, item: Any) -> bool:
        """Check if item is in buffer"""
        return item in self.items
    
    def clear(self) -> None:
        """Clear buffer"""
        self.items.clear()
    
    def __len__(self) -> int:
        return len(self.items)
