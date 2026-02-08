"""
Performance monitoring and metrics collection
"""

import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data class"""
    
    # Processing metrics
    total_messages_processed: int = 0
    total_messages_forwarded: int = 0
    total_messages_rejected: int = 0
    
    # Timing metrics
    avg_processing_time: float = 0.0
    max_processing_time: float = 0.0
    min_processing_time: float = float('inf')
    
    # Source metrics
    messages_by_source: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Error metrics
    total_errors: int = 0
    errors_by_type: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    
    # Database metrics
    db_query_count: int = 0
    db_avg_query_time: float = 0.0
    
    # AI metrics
    ai_requests: int = 0
    ai_avg_response_time: float = 0.0
    ai_errors: int = 0
    
    # Rate limiting
    rate_limit_hits: int = 0
    
    # Timestamp
    last_reset: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """
    Performance monitoring and metrics collection
    
    Tracks:
    - Message processing times
    - Database query performance
    - AI service performance
    - Error rates
    - Source channel statistics
    """
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self._processing_times = []
        self._db_query_times = []
        self._ai_response_times = []
        
        # Hourly metrics for trending
        self.hourly_metrics: Dict[str, PerformanceMetrics] = {}
        
        logger.info("Performance monitor initialized")
    
    def record_message_processed(
        self,
        processing_time: float,
        source: str,
        forwarded: bool = False
    ) -> None:
        """
        Record message processing
        
        Args:
            processing_time: Time taken to process in seconds
            source: Source channel
            forwarded: Whether message was forwarded
        """
        self.metrics.total_messages_processed += 1
        
        if forwarded:
            self.metrics.total_messages_forwarded += 1
        else:
            self.metrics.total_messages_rejected += 1
        
        # Update timing metrics
        self._processing_times.append(processing_time)
        self.metrics.max_processing_time = max(
            self.metrics.max_processing_time,
            processing_time
        )
        self.metrics.min_processing_time = min(
            self.metrics.min_processing_time,
            processing_time
        )
        self.metrics.avg_processing_time = sum(self._processing_times) / len(self._processing_times)
        
        # Update source metrics
        self.metrics.messages_by_source[source] += 1
        
        # Keep only last 1000 samples
        if len(self._processing_times) > 1000:
            self._processing_times = self._processing_times[-1000:]
    
    def record_error(self, error_type: str) -> None:
        """
        Record error occurrence
        
        Args:
            error_type: Type/category of error
        """
        self.metrics.total_errors += 1
        self.metrics.errors_by_type[error_type] += 1
    
    def record_db_query(self, query_time: float) -> None:
        """
        Record database query
        
        Args:
            query_time: Query execution time in seconds
        """
        self.metrics.db_query_count += 1
        self._db_query_times.append(query_time)
        
        self.metrics.db_avg_query_time = sum(self._db_query_times) / len(self._db_query_times)
        
        # Keep only last 1000 samples
        if len(self._db_query_times) > 1000:
            self._db_query_times = self._db_query_times[-1000:]
    
    def record_ai_request(self, response_time: float, error: bool = False) -> None:
        """
        Record AI service request
        
        Args:
            response_time: Response time in seconds
            error: Whether request resulted in error
        """
        self.metrics.ai_requests += 1
        
        if error:
            self.metrics.ai_errors += 1
        else:
            self._ai_response_times.append(response_time)
            self.metrics.ai_avg_response_time = sum(self._ai_response_times) / len(self._ai_response_times)
        
        # Keep only last 1000 samples
        if len(self._ai_response_times) > 1000:
            self._ai_response_times = self._ai_response_times[-1000:]
    
    def record_rate_limit_hit(self) -> None:
        """Record rate limit hit"""
        self.metrics.rate_limit_hits += 1
    
    def get_metrics(self) -> Dict:
        """
        Get current metrics
        
        Returns:
            Dictionary with all metrics
        """
        uptime = (datetime.now() - self.metrics.last_reset).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "processing": {
                "total_processed": self.metrics.total_messages_processed,
                "total_forwarded": self.metrics.total_messages_forwarded,
                "total_rejected": self.metrics.total_messages_rejected,
                "forward_rate": (
                    self.metrics.total_messages_forwarded / self.metrics.total_messages_processed
                    if self.metrics.total_messages_processed > 0 else 0
                ),
                "avg_time_ms": round(self.metrics.avg_processing_time * 1000, 2),
                "max_time_ms": round(self.metrics.max_processing_time * 1000, 2),
                "min_time_ms": round(self.metrics.min_processing_time * 1000, 2) if self.metrics.min_processing_time != float('inf') else 0,
                "messages_per_minute": (
                    self.metrics.total_messages_processed / (uptime / 60)
                    if uptime > 0 else 0
                )
            },
            "sources": dict(self.metrics.messages_by_source),
            "errors": {
                "total": self.metrics.total_errors,
                "by_type": dict(self.metrics.errors_by_type),
                "error_rate": (
                    self.metrics.total_errors / self.metrics.total_messages_processed
                    if self.metrics.total_messages_processed > 0 else 0
                )
            },
            "database": {
                "query_count": self.metrics.db_query_count,
                "avg_query_time_ms": round(self.metrics.db_avg_query_time * 1000, 2),
                "queries_per_message": (
                    self.metrics.db_query_count / self.metrics.total_messages_processed
                    if self.metrics.total_messages_processed > 0 else 0
                )
            },
            "ai": {
                "requests": self.metrics.ai_requests,
                "errors": self.metrics.ai_errors,
                "avg_response_time_ms": round(self.metrics.ai_avg_response_time * 1000, 2),
                "error_rate": (
                    self.metrics.ai_errors / self.metrics.ai_requests
                    if self.metrics.ai_requests > 0 else 0
                )
            },
            "rate_limiting": {
                "hits": self.metrics.rate_limit_hits
            }
        }
    
    def get_summary(self) -> str:
        """
        Get human-readable summary
        
        Returns:
            Formatted summary string
        """
        metrics = self.get_metrics()
        
        summary = f"""
Performance Summary:
-------------------
Uptime: {metrics['uptime_seconds']:.0f}s

Processing:
  - Total: {metrics['processing']['total_processed']}
  - Forwarded: {metrics['processing']['total_forwarded']}
  - Rejected: {metrics['processing']['total_rejected']}
  - Forward Rate: {metrics['processing']['forward_rate']:.1%}
  - Avg Time: {metrics['processing']['avg_time_ms']}ms
  - Throughput: {metrics['processing']['messages_per_minute']:.1f} msg/min

Errors:
  - Total: {metrics['errors']['total']}
  - Error Rate: {metrics['errors']['error_rate']:.1%}

Database:
  - Queries: {metrics['database']['query_count']}
  - Avg Time: {metrics['database']['avg_query_time_ms']}ms

AI:
  - Requests: {metrics['ai']['requests']}
  - Errors: {metrics['ai']['errors']}
  - Avg Time: {metrics['ai']['avg_response_time_ms']}ms
"""
        return summary
    
    def reset_metrics(self) -> None:
        """Reset all metrics"""
        self.metrics = PerformanceMetrics()
        self._processing_times = []
        self._db_query_times = []
        self._ai_response_times = []
        logger.info("Performance metrics reset")
    
    def log_summary(self) -> None:
        """Log performance summary"""
        logger.info(self.get_summary())


# Context managers for timing
class TimedOperation:
    """Context manager for timing operations"""
    
    def __init__(self, monitor: PerformanceMonitor, operation_type: str):
        self.monitor = monitor
        self.operation_type = operation_type
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        
        if self.operation_type == "db":
            self.monitor.record_db_query(elapsed)
        elif self.operation_type == "ai":
            self.monitor.record_ai_request(elapsed, error=exc_type is not None)
        
        return False  # Don't suppress exceptions


# Global instance
_performance_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor
