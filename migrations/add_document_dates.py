"""
Migration: Add effective_date and end_date columns to documents table
"""
from foundation.clients import SnowflakeClient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """Add date fields to documents table"""
    try:
        snowflake = SnowflakeClient()

        # Add effective_date column
        logger.info("Adding effective_date column to documents table...")
        snowflake.execute_query("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS effective_date DATE
        """)

        # Add end_date column
        logger.info("Adding end_date column to documents table...")
        snowflake.execute_query("""
            ALTER TABLE documents
            ADD COLUMN IF NOT EXISTS end_date DATE
        """)

        logger.info("✓ Migration completed successfully!")
        return True

    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("Migration completed successfully")
    else:
        print("Migration failed")
