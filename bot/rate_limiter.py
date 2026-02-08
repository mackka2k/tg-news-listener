"""
Rate limiting to prevent Telegram API abuse
"""

import asyncio
import logging
from datetime import datetime, timedelta
from collections import deque
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with exponential backoff
    """
    
    def __init__(
        self,
        max_per_minute: int = 20,
        max_per_hour: int = 100,
        burst_size: int = 5
    ):
        """
        Initialize rate limiter
        
        Args:
            max_per_minute: Maximum requests per minute
            max_per_hour: Maximum requests per hour
            burst_size: Maximum burst size
        """
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.burst_size = burst_size
        
        self.minute_timestamps = deque(maxlen=max_per_minute)
        self.hour_timestamps = deque(maxlen=max_per_hour)
        
        self.consecutive_waits = 0
        self.last_wait_time = 0
        
        logger.info(
            f"Rate limiter initialized: {max_per_minute}/min, {max_per_hour}/hour, "
            f"burst={burst_size}"
        )
    
    async def acquire(self) -> None:
        """
        Acquire permission to make a request
        Will wait if rate limit is exceeded
        """
        now = datetime.now()
        
        # Clean old timestamps
        self._clean_old_timestamps(now)
        
        # Check minute limit
        if len(self.minute_timestamps) >= self.max_per_minute:
            wait_time = self._calculate_wait_time(self.minute_timestamps, 60)
            logger.warning(f"Rate limit (minute): waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            self.consecutive_waits += 1
        
        # Check hour limit
        elif len(self.hour_timestamps) >= self.max_per_hour:
            wait_time = self._calculate_wait_time(self.hour_timestamps, 3600)
            logger.warning(f"Rate limit (hour): waiting {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
            self.consecutive_waits += 1
        
        else:
            # No wait needed, reset consecutive waits
            self.consecutive_waits = 0
        
        # Record timestamp
        now = datetime.now()
        self.minute_timestamps.append(now)
        self.hour_timestamps.append(now)
    
    def _clean_old_timestamps(self, now: datetime) -> None:
        """Remove timestamps older than their respective windows"""
        # Clean minute window
        while self.minute_timestamps and (now - self.minute_timestamps[0]) > timedelta(seconds=60):
            self.minute_timestamps.popleft()
        
        # Clean hour window
        while self.hour_timestamps and (now - self.hour_timestamps[0]) > timedelta(seconds=3600):
            self.hour_timestamps.popleft()
    
    def _calculate_wait_time(self, timestamps: deque, window_seconds: int) -> float:
        """
        Calculate how long to wait before next request
        
        Args:
            timestamps: Deque of timestamps
            window_seconds: Time window in seconds
        
        Returns:
            Wait time in seconds
        """
        if not timestamps:
            return 0
        
        oldest = timestamps[0]
        elapsed = (datetime.now() - oldest).total_seconds()
        wait_time = window_seconds - elapsed + 1  # +1 for safety margin
        
        # Apply exponential backoff if consecutive waits
        if self.consecutive_waits > 0:
            backoff_multiplier = min(2 ** self.consecutive_waits, 8)  # Max 8x
            wait_time *= backoff_multiplier
            logger.debug(f"Exponential backoff: {backoff_multiplier}x")
        
        return max(wait_time, 0)
    
    async def handle_flood_wait(self, wait_seconds: int) -> None:
        """
        Handle Telegram FloodWaitError
        
        Args:
            wait_seconds: Seconds to wait as specified by Telegram
        """
        logger.warning(f"FloodWaitError: waiting {wait_seconds}s as requested by Telegram")
        
        # Add some buffer time
        wait_with_buffer = wait_seconds + 5
        
        await asyncio.sleep(wait_with_buffer)
        
        # Reset rate limiter state
        self.minute_timestamps.clear()
        self.hour_timestamps.clear()
        self.consecutive_waits = 0
        
        logger.info("FloodWait completed, rate limiter reset")
    
    def get_stats(self) -> dict:
        """
        Get current rate limiter statistics
        
        Returns:
            Dictionary with stats
        """
        now = datetime.now()
        self._clean_old_timestamps(now)
        
        return {
            'requests_last_minute': len(self.minute_timestamps),
            'requests_last_hour': len(self.hour_timestamps),
            'max_per_minute': self.max_per_minute,
            'max_per_hour': self.max_per_hour,
            'consecutive_waits': self.consecutive_waits,
        }
