"""Initialize Snowflake database schema for Asset Management Platform"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import foundation
sys.path.insert(0, str(Path(__file__).parent.parent))

from foundation.clients import SnowflakeClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def read_schema_file():
    """Read the schema.sql file"""
    schema_path = Path(__file__).parent.parent / 'database' / 'schema.sql'

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    with open(schema_path, 'r') as f:
        return f.read()


def execute_schema_statements(snowflake: SnowflakeClient, schema_sql: str):
    """Execute each SQL statement in the schema file"""
    # Split by semicolon and filter out comments and empty statements
    statements = []
    current_statement = []

    for line in schema_sql.split('\n'):
        # Skip comment lines
        if line.strip().startswith('--'):
            continue

        current_statement.append(line)

        # If line ends with semicolon, we have a complete statement
        if line.strip().endswith(';'):
            stmt = '\n'.join(current_statement).strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
            current_statement = []

    # Execute each statement
    results = {'success': 0, 'failed': 0}

    for stmt in statements:
        if not stmt.strip():
            continue

        try:
            # Extract table name for logging
            table_name = None
            if 'CREATE TABLE' in stmt:
                parts = stmt.split('CREATE TABLE IF NOT EXISTS')
                if len(parts) > 1:
                    table_name = parts[1].split('(')[0].strip()

            logger.info(f"Executing: {'CREATE TABLE ' + table_name if table_name else 'SQL statement'}")
            snowflake.execute_query(stmt)
            results['success'] += 1

            if table_name:
                logger.info(f"✓ Created table: {table_name}")

        except Exception as e:
            logger.error(f"✗ Failed to execute statement: {e}", exc_info=True)
            results['failed'] += 1
            continue

    return results


def verify_tables(snowflake: SnowflakeClient):
    """Verify that all expected tables exist"""
    expected_tables = [
        'ENTITIES',
        'BUILDINGS',
        'BUDGET_ITEMS',
        'DOCUMENTS',
        'SHARE_TOKENS'
    ]

    logger.info("\nVerifying tables...")

    try:
        query = "SHOW TABLES IN your-database-name.PUBLIC"
        results = snowflake.execute_query(query)

        existing_tables = [row['name'].upper() for row in results]

        for table in expected_tables:
            if table in existing_tables:
                logger.info(f"✓ Table exists: {table}")
            else:
                logger.warning(f"✗ Table missing: {table}")

    except Exception as e:
        logger.error(f"Failed to verify tables: {e}", exc_info=True)


def main():
    """Main initialization function"""
    logger.info("=" * 60)
    logger.info("Asset Management Platform - Database Initialization")
    logger.info("=" * 60)

    try:
        # Initialize Snowflake client
        logger.info("\nConnecting to Snowflake...")
        snowflake = SnowflakeClient()
        logger.info("✓ Connected to Snowflake")

        # Read schema file
        logger.info("\nReading schema file...")
        schema_sql = read_schema_file()
        logger.info("✓ Schema file loaded")

        # Execute schema statements
        logger.info("\nExecuting schema statements...")
        results = execute_schema_statements(snowflake, schema_sql)

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info(f"Summary: {results['success']} succeeded, {results['failed']} failed")
        logger.info("=" * 60)

        # Verify tables
        verify_tables(snowflake)

        logger.info("\n✓ Database initialization completed successfully")
        return 0

    except Exception as e:
        logger.error(f"\n✗ Database initialization failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
