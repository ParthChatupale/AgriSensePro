"""
Migration script to add crop and category columns to posts table.
Run this script to update your database schema.
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import app's database connection
from app.database import engine
from sqlalchemy import text

def run_migration():
    """Run the migration to add crop and category columns."""
    try:
        print("🔌 Connecting to database...")
        
        # Read migration SQL
        migration_file = BASE_DIR / "migrations" / "add_post_crop_category.sql"
        if not migration_file.exists():
            print(f"❌ Migration file not found: {migration_file}")
            sys.exit(1)
        
        with open(migration_file, "r") as f:
            migration_sql = f.read()
        
        # Execute migration
        print("📝 Running migration: add_post_crop_category.sql")
        with engine.connect() as conn:
            # Execute each statement separately
            statements = [s.strip() for s in migration_sql.split(";") if s.strip() and not s.strip().startswith("--")]
            for statement in statements:
                if statement:
                    try:
                        conn.execute(text(statement))
                        conn.commit()
                        print(f"   ✓ Executed: {statement[:50]}...")
                    except Exception as e:
                        # Ignore "column already exists" errors
                        error_msg = str(e).lower()
                        if "already exists" in error_msg or "duplicate" in error_msg or "if not exists" in error_msg:
                            print(f"   ⚠️  Skipped (already exists): {statement[:50]}...")
                        else:
                            print(f"   ❌ Error: {e}")
                            raise
        
        print("\n✅ Migration completed successfully!")
        print("   - Added 'crop' column to posts table")
        print("   - Added 'category' column to posts table")
        print("   - Created indexes for faster filtering")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

