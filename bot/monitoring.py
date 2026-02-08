"""
Monitoring and observability with Sentry and Prometheus
"""

import logging
import sentry_sdk
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from typing import Optional
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)


# Prometheus metrics
messages_received = Counter(
    'bot_messages_received_total',
    'Total messages received from source channels',
    ['source_channel']
)

messages_forwarded = Counter(
    'bot_messages_forwarded_total',
    'Total messages forwarded to target channel'
)

messages_rejected = Counter(
    'bot_messages_rejected_total',
    'Total messages rejected',
    ['reason']
)

errors_total = Counter(
    'bot_errors_total',
    'Total errors encountered',
    ['error_type']
)

daily_post_count = Gauge(
    'bot_daily_posts',
    'Current number of posts today'
)

processing_time = Histogram(
    'bot_message_processing_seconds',
    'Time spent processing messages'
)

rate_limiter_waits = Counter(
    'bot_rate_limiter_waits_total',
    'Total rate limiter waits'
)

database_operations = Histogram(
    'bot_database_operation_seconds',
    'Time spent on database operations',
    ['operation']
)


class Monitoring:
    """
    Centralized monitoring and observability
    """
    
    def __init__(self, sentry_dsn: Optional[str] = None, environment: str = "development"):
        """
        Initialize monitoring
        
        Args:
            sentry_dsn: Sentry DSN for error tracking
            environment: Environment name (development/production)
        """
        self.environment = environment
        self.sentry_enabled = False
        
        # Initialize Sentry if DSN provided
        if sentry_dsn:
            try:
                sentry_sdk.init(
                    dsn=sentry_dsn,
                    environment=environment,
                    traces_sample_rate=0.1 if environment == "production" else 1.0,
                    profiles_sample_rate=0.1 if environment == "production" else 1.0,
                )
                self.sentry_enabled = True
                logger.info(f"Sentry initialized for environment: {environment}")
            except Exception as e:
                logger.warning(f"Failed to initialize Sentry: {e}")
        else:
            logger.info("Sentry not configured (no DSN provided)")
    
    def record_message_received(self, source_channel: str) -> None:
        """Record message received from source channel"""
        messages_received.labels(source_channel=source_channel).inc()
    
    def record_message_forwarded(self) -> None:
        """Record message forwarded"""
        messages_forwarded.inc()
    
    def record_message_rejected(self, reason: str) -> None:
        """Record message rejected"""
        # Normalize reason for better grouping
        normalized_reason = reason.split(':')[0] if ':' in reason else reason
        messages_rejected.labels(reason=normalized_reason).inc()
    
    def record_error(self, error_type: str, error: Exception = None) -> None:
        """
        Record error
        
        Args:
            error_type: Type of error
            error: Optional exception object
        """
        errors_total.labels(error_type=error_type).inc()
        
        if self.sentry_enabled and error:
            sentry_sdk.capture_exception(error)
    
    def update_daily_post_count(self, count: int) -> None:
        """Update daily post count gauge"""
        daily_post_count.set(count)
    
    def record_rate_limiter_wait(self) -> None:
        """Record rate limiter wait"""
        rate_limiter_waits.inc()
    
    @contextmanager
    def measure_processing_time(self):
        """Context manager to measure message processing time"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            processing_time.observe(duration)
    
    @contextmanager
    def measure_database_operation(self, operation: str):
        """Context manager to measure database operation time"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            database_operations.labels(operation=operation).observe(duration)
    
    def get_metrics(self) -> bytes:
        """
        Get Prometheus metrics in text format
        
        Returns:
            Metrics as bytes
        """
        return generate_latest()
    
    def get_content_type(self) -> str:
        """Get Prometheus content type"""
        return CONTENT_TYPE_LATEST
    
    def capture_message(self, message: str, level: str = "info") -> None:
        """
        Capture message in Sentry
        
        Args:
            message: Message to capture
            level: Log level (info, warning, error)
        """
        if self.sentry_enabled:
            sentry_sdk.capture_message(message, level=level)
    
    def set_user_context(self, user_id: int, username: str = None) -> None:
        """
        Set user context for Sentry
        
        Args:
            user_id: Telegram user ID
            username: Optional username
        """
        if self.sentry_enabled:
            sentry_sdk.set_user({
                "id": user_id,
                "username": username
            })
    
    def add_breadcrumb(self, message: str, category: str = "default", level: str = "info") -> None:
        """
        Add breadcrumb for debugging
        
        Args:
            message: Breadcrumb message
            category: Category
            level: Log level
        """
        if self.sentry_enabled:
            sentry_sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level
            )
