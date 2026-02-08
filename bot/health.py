"""
Health check HTTP server for liveness and readiness probes
"""

import asyncio
import logging
from aiohttp import web
from typing import Optional, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class HealthCheckServer:
    """
    HTTP server for health checks and metrics
    """
    
    def __init__(
        self,
        port: int = 8080,
        monitoring = None,
        storage = None
    ):
        """
        Initialize health check server
        
        Args:
            port: Port to listen on
            monitoring: Monitoring instance for metrics
            storage: Storage instance for database health
        """
        self.port = port
        self.monitoring = monitoring
        self.storage = storage
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        
        self.start_time = datetime.now()
        self.is_ready = False
        self.last_message_time: Optional[datetime] = None
        
        # Setup routes
        self.app.router.add_get('/', self.health_handler)  # Root redirects to health
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/ready', self.ready_handler)
        self.app.router.add_get('/metrics', self.metrics_handler)
        self.app.router.add_get('/stats', self.stats_handler)
        
        logger.info(f"Health check server configured on port {port}")
    
    async def start(self) -> None:
        """Start the health check server"""
        try:
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()
            self.site = web.TCPSite(self.runner, '0.0.0.0', self.port)
            await self.site.start()
            logger.info(f"Health check server started on http://0.0.0.0:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start health check server: {e}")
            raise
    
    async def stop(self) -> None:
        """Stop the health check server"""
        if self.site:
            await self.site.stop()
        if self.runner:
            await self.runner.cleanup()
        logger.info("Health check server stopped")
    
    def mark_ready(self) -> None:
        """Mark service as ready"""
        self.is_ready = True
        logger.info("Service marked as ready")
    
    def mark_not_ready(self) -> None:
        """Mark service as not ready"""
        self.is_ready = False
        logger.warning("Service marked as not ready")
    
    def record_message_processed(self) -> None:
        """Record that a message was processed"""
        self.last_message_time = datetime.now()
    
    async def health_handler(self, request: web.Request) -> web.Response:
        """
        Liveness probe - checks if service is alive
        
        Returns 200 if service is running
        """
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        health_data = {
            'status': 'healthy',
            'uptime_seconds': int(uptime),
            'timestamp': datetime.now().isoformat()
        }
        
        return web.json_response(health_data, status=200)
    
    async def ready_handler(self, request: web.Request) -> web.Response:
        """
        Readiness probe - checks if service is ready to handle requests
        
        Returns 200 if ready, 503 if not ready
        """
        if not self.is_ready:
            return web.json_response(
                {'status': 'not_ready', 'reason': 'Service not initialized'},
                status=503
            )
        
        # Check database connection
        db_healthy = True
        if self.storage:
            try:
                # Simple database check
                await self.storage.get_today_post_count()
            except Exception as e:
                logger.error(f"Database health check failed: {e}")
                db_healthy = False
        
        if not db_healthy:
            return web.json_response(
                {'status': 'not_ready', 'reason': 'Database not healthy'},
                status=503
            )
        
        ready_data = {
            'status': 'ready',
            'database': 'healthy',
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return web.json_response(ready_data, status=200)
    
    async def metrics_handler(self, request: web.Request) -> web.Response:
        """
        Prometheus metrics endpoint
        
        Returns metrics in Prometheus text format
        """
        if not self.monitoring:
            return web.Response(text="Monitoring not configured", status=503)
        
        try:
            metrics = self.monitoring.get_metrics()
            content_type = self.monitoring.get_content_type()
            return web.Response(body=metrics, content_type=content_type)
        except Exception as e:
            logger.error(f"Failed to generate metrics: {e}")
            return web.Response(text=f"Error: {e}", status=500)
    
    async def stats_handler(self, request: web.Request) -> web.Response:
        """
        Statistics endpoint - human-readable stats
        
        Returns JSON with current statistics
        """
        stats = {
            'uptime_seconds': int((datetime.now() - self.start_time).total_seconds()),
            'ready': self.is_ready,
            'last_message_time': self.last_message_time.isoformat() if self.last_message_time else None,
        }
        
        # Add database stats if available
        if self.storage:
            try:
                db_stats = await self.storage.get_stats()
                stats['database'] = db_stats
            except Exception as e:
                logger.error(f"Failed to get database stats: {e}")
                stats['database'] = {'error': str(e)}
        
        # Add performance metrics
        from bot.performance import get_performance_monitor
        monitor = get_performance_monitor()
        stats['performance'] = monitor.get_metrics()
        
        return web.json_response(stats, status=200)
