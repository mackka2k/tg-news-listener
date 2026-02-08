"""
Database storage layer for persistent state management
"""

import aiosqlite
import logging
from datetime import datetime, date
from typing import Optional, Set
from pathlib import Path

logger = logging.getLogger(__name__)


class Storage:
    """
    SQLite-based storage for bot state
    """
    
    def __init__(self, db_path: str = "bot.db"):
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
    
    async def initialize(self) -> None:
        """
        Initialize database connection and create tables
        """
        logger.info(f"Initializing database: {self.db_path}")
        
        # Create database file if it doesn't exist
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        
        await self._create_tables()
        await self._run_migrations()
        
        logger.info("Database initialized successfully")
    
    async def _create_tables(self) -> None:
        """Create database tables if they don't exist"""
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS forwarded_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                source_channel TEXT NOT NULL,
                forwarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE UNIQUE NOT NULL,
                posts_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_forwarded_messages_id 
            ON forwarded_messages(message_id)
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_forwarded_messages_date 
            ON forwarded_messages(forwarded_at)
        """)
        
        await self.db.execute("""
            CREATE INDEX IF NOT EXISTS idx_daily_stats_date 
            ON daily_stats(date)
        """)
        
        await self.db.commit()
    
    async def _run_migrations(self) -> None:
        """Run database migrations"""
        # Get current version
        cursor = await self.db.execute("SELECT MAX(version) as version FROM schema_version")
        row = await cursor.fetchone()
        current_version = row['version'] if row and row['version'] else 0
        
        logger.info(f"Current schema version: {current_version}")
        
        # Add future migrations here
        # if current_version < 1:
        #     await self._migrate_to_v1()
        
        await self.db.commit()
    
    async def is_message_forwarded(self, message_id: str) -> bool:
        """
        Check if message has already been forwarded
        
        Args:
            message_id: Unique message identifier (format: chat_id_message_id)
        
        Returns:
            True if message was already forwarded
        """
        cursor = await self.db.execute(
            "SELECT 1 FROM forwarded_messages WHERE message_id = ? LIMIT 1",
            (message_id,)
        )
        result = await cursor.fetchone()
        return result is not None
    
    async def mark_message_forwarded(
        self,
        message_id: str,
        source_channel: str,
        message_text: Optional[str] = None
    ) -> None:
        """
        Mark message as forwarded
        
        Args:
            message_id: Unique message identifier
            source_channel: Source channel name/ID
            message_text: Optional message text for reference
        """
        try:
            await self.db.execute(
                """
                INSERT INTO forwarded_messages (message_id, source_channel, message_text)
                VALUES (?, ?, ?)
                """,
                (message_id, source_channel, message_text[:500] if message_text else None)
            )
            await self.db.commit()
        except aiosqlite.IntegrityError:
            # Message already exists, ignore
            logger.debug(f"Message {message_id} already marked as forwarded")
    
    async def get_today_post_count(self) -> int:
        """
        Get number of posts forwarded today
        
        Returns:
            Number of posts today
        """
        today = date.today().isoformat()
        
        cursor = await self.db.execute(
            "SELECT posts_count FROM daily_stats WHERE date = ?",
            (today,)
        )
        row = await cursor.fetchone()
        
        return row['posts_count'] if row else 0
    
    async def increment_today_post_count(self) -> int:
        """
        Increment today's post count
        
        Returns:
            New post count for today
        """
        today = date.today().isoformat()
        
        # Insert or update
        await self.db.execute(
            """
            INSERT INTO daily_stats (date, posts_count)
            VALUES (?, 1)
            ON CONFLICT(date) DO UPDATE SET
                posts_count = posts_count + 1,
                updated_at = CURRENT_TIMESTAMP
            """,
            (today,)
        )
        await self.db.commit()
        
        return await self.get_today_post_count()
    
    async def reset_daily_counter(self) -> None:
        """
        Reset daily counter (called at midnight or on new day)
        """
        today = date.today().isoformat()
        
        await self.db.execute(
            """
            INSERT OR IGNORE INTO daily_stats (date, posts_count)
            VALUES (?, 0)
            """,
            (today,)
        )
        await self.db.commit()
        
        logger.info(f"Daily counter reset for {today}")
    
    async def cleanup_old_messages(self, days: int = 30) -> int:
        """
        Clean up old forwarded messages
        
        Args:
            days: Number of days to keep
        
        Returns:
            Number of deleted records
        """
        cursor = await self.db.execute(
            """
            DELETE FROM forwarded_messages
            WHERE forwarded_at < datetime('now', '-' || ? || ' days')
            """,
            (days,)
        )
        await self.db.commit()
        
        deleted = cursor.rowcount
        logger.info(f"Cleaned up {deleted} old messages (older than {days} days)")
        
        return deleted
    
    async def get_recent_messages(self, limit: int = 20) -> list:
        """
        Get recent forwarded messages for deduplication
        
        Args:
            limit: Number of messages to retrieve
        
        Returns:
            List of message texts
        """
        cursor = await self.db.execute(
            """
            SELECT message_text FROM forwarded_messages
            WHERE message_text IS NOT NULL
            ORDER BY forwarded_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        rows = await cursor.fetchall()
        return [row['message_text'] for row in rows]

    async def get_stats(self) -> dict:
        """
        Get database statistics
        
        Returns:
            Dictionary with stats
        """
        # Total forwarded messages
        cursor = await self.db.execute("SELECT COUNT(*) as count FROM forwarded_messages")
        row = await cursor.fetchone()
        total_messages = row['count']
        
        # Today's count
        today_count = await self.get_today_post_count()
        
        # Messages in last 7 days
        cursor = await self.db.execute(
            """
            SELECT COUNT(*) as count FROM forwarded_messages
            WHERE forwarded_at >= datetime('now', '-7 days')
            """
        )
        row = await cursor.fetchone()
        last_7_days = row['count']
        
        return {
            'total_messages': total_messages,
            'today_count': today_count,
            'last_7_days': last_7_days,
        }
    
    async def close(self) -> None:
        """Close database connection"""
        if self.db:
            await self.db.close()
            logger.info("Database connection closed")
