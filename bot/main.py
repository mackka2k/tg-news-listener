"""
Main entry point for the Telegram News Bot
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from bot.config import Config
from bot.storage import Storage
from bot.monitoring import Monitoring
from bot.health import HealthCheckServer
from bot.client import NewsBot


def setup_logging(log_level: str = "INFO") -> None:
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/bot.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce noise from libraries
    logging.getLogger('telethon').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)


async def main() -> None:
    """Main entry point"""
    # Load configuration
    try:
        config = Config.from_env()
        print(f"✅ Configuration loaded (Environment: {config.ENVIRONMENT})")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    # Setup logging
    setup_logging(config.LOG_LEVEL)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("🤖 Telegram News Bot v2.0 - Production Ready")
    logger.info("=" * 60)
    
    # Run database migrations
    from bot.migrations import MigrationManager
    try:
        migration_manager = MigrationManager(config.DATABASE_PATH)
        pending = migration_manager.get_pending_migrations()
        if pending:
            logger.info(f"Applying {len(pending)} pending migrations...")
            migration_manager.migrate()
        else:
            logger.info("Database schema is up to date")
        migration_manager.close()
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)
        
    # Initialize services
    storage = Storage(db_path=config.DATABASE_PATH)
    monitoring = Monitoring(
        sentry_dsn=config.SENTRY_DSN,
        environment=config.ENVIRONMENT
    )
    health_server = HealthCheckServer(
        port=config.METRICS_PORT,
        monitoring=monitoring,
        storage=storage
    )
    
    # Create bot instance
    bot = NewsBot(
        config=config,
        storage=storage,
        monitoring=monitoring,
        health_server=health_server
    )
    
    
    # Stop event for graceful shutdown
    stop_event = asyncio.Event()

    # Define simple handler
    def request_stop():
        logger.info("🛑 Stop signal received, shutting down gracefully...")
        stop_event.set()

    if sys.platform != 'win32':
        # Use asyncio signal handlers on Linux/Mac
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, request_stop)
        loop.add_signal_handler(signal.SIGTERM, request_stop)
    else:
        # Windows doesn't support add_signal_handler
        # We rely on KeyboardInterrupt for local dev
        pass

    try:
        logger.info("🚀 Starting NewsBot...")
        
        # Run bot in background task
        bot_task = asyncio.create_task(bot.start())
        
        # Monitor stop event
        # On Windows, we need to poll to catch KeyboardInterrupt
        while not stop_event.is_set():
            if bot_task.done():
                if bot_task.exception():
                    raise bot_task.exception()
                break
            await asyncio.sleep(0.5)
            
    except asyncio.CancelledError:
        logger.info("Main task cancelled")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        monitoring.record_error("fatal_error", e)
        sys.exit(1)
    finally:
        logger.info("🛑 Shutting down...")
        await bot.shutdown()


if __name__ == "__main__":
    # Windows compatibility for asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
