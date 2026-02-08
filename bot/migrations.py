"""
Database migration utilities

Simple migration system for SQLite database schema changes.
"""

import logging
import sqlite3
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)


class Migration:
    """Base class for database migrations"""
    
    version: int = 0
    description: str = ""
    
    def up(self, conn: sqlite3.Connection) -> None:
        """Apply migration"""
        raise NotImplementedError
    
    def down(self, conn: sqlite3.Connection) -> None:
        """Revert migration"""
        raise NotImplementedError


class Migration001_InitialSchema(Migration):
    """Initial database schema"""
    
    version = 1
    description = "Initial schema with forwarded_messages and daily_stats"
    
    def up(self, conn: sqlite3.Connection) -> None:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS forwarded_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id TEXT UNIQUE NOT NULL,
                source_channel TEXT NOT NULL,
                content TEXT,
                forwarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                post_count INTEGER DEFAULT 0
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_forwarded_date 
            ON forwarded_messages(forwarded_at)
        """)
        
        conn.commit()
    
    def down(self, conn: sqlite3.Connection) -> None:
        conn.execute("DROP TABLE IF EXISTS forwarded_messages")
        conn.execute("DROP TABLE IF EXISTS daily_stats")
        conn.commit()


class Migration002_AddMetadata(Migration):
    """Add metadata columns for better tracking"""
    
    version = 2
    description = "Add metadata columns to forwarded_messages"
    
    def up(self, conn: sqlite3.Connection) -> None:
        # Check if columns already exist
        cursor = conn.execute("PRAGMA table_info(forwarded_messages)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'processed_text' not in columns:
            conn.execute("""
                ALTER TABLE forwarded_messages 
                ADD COLUMN processed_text TEXT
            """)
        
        if 'tags' not in columns:
            conn.execute("""
                ALTER TABLE forwarded_messages 
                ADD COLUMN tags TEXT
            """)
        
        conn.commit()
    
    def down(self, conn: sqlite3.Connection) -> None:
        # SQLite doesn't support DROP COLUMN easily
        # Would need to recreate table
        logger.warning("Downgrade not fully supported for this migration")


# Registry of all migrations in order
MIGRATIONS: List[Migration] = [
    Migration001_InitialSchema(),
    Migration002_AddMetadata(),
]


class MigrationManager:
    """Manages database migrations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._ensure_migration_table()
    
    def _ensure_migration_table(self) -> None:
        """Create migrations tracking table"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                description TEXT,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def get_current_version(self) -> int:
        """Get current schema version"""
        cursor = self.conn.execute(
            "SELECT MAX(version) FROM schema_migrations"
        )
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations"""
        current = self.get_current_version()
        return [m for m in MIGRATIONS if m.version > current]
    
    def migrate(self, target_version: int = None) -> None:
        """Run pending migrations up to target version"""
        current = self.get_current_version()
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info(f"Database is up to date (version {current})")
            return
        
        for migration in pending:
            if target_version and migration.version > target_version:
                break
            
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            
            try:
                migration.up(self.conn)
                
                self.conn.execute(
                    "INSERT INTO schema_migrations (version, description) VALUES (?, ?)",
                    (migration.version, migration.description)
                )
                self.conn.commit()
                
                logger.info(f"✅ Migration {migration.version} applied successfully")
                
            except Exception as e:
                logger.error(f"❌ Migration {migration.version} failed: {e}")
                self.conn.rollback()
                raise
    
    def rollback(self, target_version: int) -> None:
        """Rollback to target version"""
        current = self.get_current_version()
        
        if target_version >= current:
            logger.warning("Target version is >= current version, nothing to rollback")
            return
        
        migrations_to_revert = [
            m for m in reversed(MIGRATIONS)
            if target_version < m.version <= current
        ]
        
        for migration in migrations_to_revert:
            logger.info(f"Reverting migration {migration.version}: {migration.description}")
            
            try:
                migration.down(self.conn)
                
                self.conn.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,)
                )
                self.conn.commit()
                
                logger.info(f"✅ Migration {migration.version} reverted successfully")
                
            except Exception as e:
                logger.error(f"❌ Rollback {migration.version} failed: {e}")
                self.conn.rollback()
                raise
    
    def status(self) -> List[Tuple[int, str, bool]]:
        """Get migration status"""
        current = self.get_current_version()
        
        status = []
        for migration in MIGRATIONS:
            applied = migration.version <= current
            status.append((migration.version, migration.description, applied))
        
        return status
    
    def close(self) -> None:
        """Close database connection"""
        self.conn.close()


if __name__ == "__main__":
    # CLI for running migrations
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrations.py [migrate|rollback|status] [version]")
        sys.exit(1)
    
    command = sys.argv[1]
    db_path = "data/bot.db"
    
    manager = MigrationManager(db_path)
    
    if command == "migrate":
        target = int(sys.argv[2]) if len(sys.argv) > 2 else None
        manager.migrate(target)
    
    elif command == "rollback":
        if len(sys.argv) < 3:
            print("Error: rollback requires target version")
            sys.exit(1)
        target = int(sys.argv[2])
        manager.rollback(target)
    
    elif command == "status":
        print("\nMigration Status:")
        print("-" * 60)
        for version, description, applied in manager.status():
            status = "✅ Applied" if applied else "⏳ Pending"
            print(f"{version}: {description} - {status}")
        print("-" * 60)
        print(f"Current version: {manager.get_current_version()}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
    
    manager.close()
