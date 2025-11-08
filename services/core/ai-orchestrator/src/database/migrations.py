"""
Database Migration Runner for AI Security Lab v4.0
Manages schema migrations for TimescaleDB
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..services.database import DatabaseService

logger = logging.getLogger(__name__)


class MigrationRunner:
    """
    Database migration runner with tracking and rollback support.
    """
    
    def __init__(self, db: DatabaseService, migrations_dir: str = "migrations"):
        self.db = db
        self.migrations_dir = Path(migrations_dir)
        
    async def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        try:
            query = "SELECT version FROM migrations ORDER BY id"
            results = await self.db.fetch_all(query)
            return [r['version'] for r in results]
        except Exception as e:
            logger.error(f"Failed to get applied migrations: {e}")
            # If migrations table doesn't exist, return empty list
            return []
    
    async def is_migration_applied(self, version: str) -> bool:
        """Check if specific migration has been applied."""
        applied = await self.get_applied_migrations()
        return version in applied
    
    async def get_pending_migrations(self) -> List[Path]:
        """Get list of migration files that haven't been applied."""
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        applied = await self.get_applied_migrations()
        
        # Get all SQL files
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        # Filter out applied migrations
        pending = []
        for file in migration_files:
            # Extract version from filename (e.g., 001_initial_schema.sql -> 001)
            version = file.stem.split('_')[0]
            if version not in applied:
                pending.append(file)
        
        return pending
    
    async def apply_migration(self, migration_file: Path) -> bool:
        """
        Apply a single migration file.
        
        Args:
            migration_file: Path to migration SQL file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract version and name from filename
            filename = migration_file.stem
            parts = filename.split('_', 1)
            version = parts[0]
            name = parts[1] if len(parts) > 1 else filename
            
            logger.info(f"Applying migration {version}: {name}")
            
            # Read migration file
            sql_content = migration_file.read_text()
            
            # Track start time
            start_time = datetime.utcnow()
            
            # Execute migration
            async with self.db.transaction() as conn:
                await conn.execute(sql_content)
            
            # Calculate execution time
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Record migration (if not already recorded)
            try:
                await self.db.execute(
                    """
                    INSERT INTO migrations (version, name, applied_at, execution_time_ms)
                    VALUES ($1, $2, NOW(), $3)
                    ON CONFLICT (version) DO NOTHING
                    """,
                    version,
                    name,
                    execution_time
                )
            except Exception as e:
                logger.warning(f"Could not record migration (table may not exist yet): {e}")
            
            logger.info(f"✅ Migration {version} applied successfully ({execution_time:.2f}ms)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration_file.name}: {e}")
            return False
    
    async def apply_all_pending(self) -> Dict[str, Any]:
        """
        Apply all pending migrations.
        
        Returns:
            Dictionary with results
        """
        pending = await self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return {
                "applied": 0,
                "failed": 0,
                "migrations": []
            }
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        results = {
            "applied": 0,
            "failed": 0,
            "migrations": []
        }
        
        for migration_file in pending:
            success = await self.apply_migration(migration_file)
            
            if success:
                results["applied"] += 1
                results["migrations"].append({
                    "file": migration_file.name,
                    "status": "success"
                })
            else:
                results["failed"] += 1
                results["migrations"].append({
                    "file": migration_file.name,
                    "status": "failed"
                })
                # Stop on first failure
                logger.error("Migration failed, stopping")
                break
        
        return results
    
    async def get_migration_status(self) -> Dict[str, Any]:
        """
        Get current migration status.
        
        Returns:
            Dictionary with migration status info
        """
        try:
            applied = await self.get_applied_migrations()
            pending = await self.get_pending_migrations()
            
            return {
                "applied_count": len(applied),
                "pending_count": len(pending),
                "applied_migrations": applied,
                "pending_migrations": [f.name for f in pending],
                "is_up_to_date": len(pending) == 0
            }
        except Exception as e:
            logger.error(f"Failed to get migration status: {e}")
            return {
                "error": str(e),
                "applied_count": 0,
                "pending_count": 0
            }
