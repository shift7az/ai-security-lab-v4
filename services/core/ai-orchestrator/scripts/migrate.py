"""
CLI tool for running database migrations
Usage: python scripts/migrate.py [command]
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.database import DatabaseService
from src.database.migrations import MigrationRunner
from src.config.settings import Settings


async def run_migrations():
    """Apply all pending migrations."""
    settings = Settings()
    
    db = DatabaseService(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_user,
        password=settings.database_password
    )
    
    try:
        print("Connecting to database...")
        await db.connect()
        
        # Get migrations directory
        migrations_dir = Path(__file__).parent.parent / "migrations"
        runner = MigrationRunner(db, str(migrations_dir))
        
        # Get status
        status = await runner.get_migration_status()
        print(f"\n{'='*60}")
        print(f"Migration Status:")
        print(f"  Applied: {status['applied_count']}")
        print(f"  Pending: {status['pending_count']}")
        print(f"{'='*60}\n")
        
        if status['pending_count'] == 0:
            print("✅ Database is up to date!")
            return
        
        print(f"Pending migrations:")
        for migration in status['pending_migrations']:
            print(f"  - {migration}")
        print()
        
        # Apply migrations
        print("Applying migrations...\n")
        results = await runner.apply_all_pending()
        
        print(f"\n{'='*60}")
        print(f"Migration Results:")
        print(f"  Applied: {results['applied']}")
        print(f"  Failed: {results['failed']}")
        print(f"{'='*60}\n")
        
        if results['failed'] > 0:
            print("❌ Some migrations failed")
            sys.exit(1)
        else:
            print("✅ All migrations applied successfully!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        await db.disconnect()


async def show_status():
    """Show migration status."""
    settings = Settings()
    
    db = DatabaseService(
        host=settings.database_host,
        port=settings.database_port,
        database=settings.database_name,
        user=settings.database_user,
        password=settings.database_password
    )
    
    try:
        await db.connect()
        
        migrations_dir = Path(__file__).parent.parent / "migrations"
        runner = MigrationRunner(db, str(migrations_dir))
        
        status = await runner.get_migration_status()
        
        print(f"\n{'='*60}")
        print("Migration Status")
        print(f"{'='*60}")
        print(f"Applied: {status['applied_count']}")
        print(f"Pending: {status['pending_count']}")
        print(f"Up to date: {'Yes' if status['is_up_to_date'] else 'No'}")
        print(f"{'='*60}\n")
        
        if status['applied_count'] > 0:
            print("Applied migrations:")
            for migration in status['applied_migrations']:
                print(f"  ✅ {migration}")
            print()
        
        if status['pending_count'] > 0:
            print("Pending migrations:")
            for migration in status['pending_migrations']:
                print(f"  ⏳ {migration}")
            print()
            
    finally:
        await db.disconnect()


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/migrate.py [up|status]")
        print()
        print("Commands:")
        print("  up      - Apply all pending migrations")
        print("  status  - Show migration status")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "up":
        asyncio.run(run_migrations())
    elif command == "status":
        asyncio.run(show_status())
    else:
        print(f"Unknown command: {command}")
        print("Use 'up' or 'status'")
        sys.exit(1)


if __name__ == "__main__":
    main()
