"""Database query functions using SnowflakeClient - Fixed for DataFrame returns"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from foundation.clients import SnowflakeClient

logger = logging.getLogger(__name__)


def _escape_sql_string(value: str) -> str:
    """Escape single quotes in SQL strings"""
    if value is None:
        return "NULL"
    return value.replace("'", "''")


def _df_to_records(df) -> List[Dict[str, Any]]:
    """Convert DataFrame to list of dictionaries, handling None/empty cases"""
    if df is None:
        return []
    try:
        if df.empty:
            return []
        return df.to_dict('records')
    except AttributeError:
        # Not a DataFrame, might already be a list
        return df if isinstance(df, list) else []


# ============================================================================
# Entity Queries
# ============================================================================

def get_all_entities() -> List[Dict[str, Any]]:
    """Get all entities ordered by creation date"""
    try:
        snowflake = SnowflakeClient()
        query = "SELECT * FROM entities ORDER BY created_at DESC"
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get entities: {e}", exc_info=True)
        return []


def get_entity_by_id(entity_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific entity by ID"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM entities WHERE entity_id = '{entity_id}'"
        results = snowflake.execute_query(query)
        records = _df_to_records(results)
        return records[0] if records else None
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}", exc_info=True)
        return None


def create_entity(name: str, description: str = None) -> str:
    """Create a new entity"""
    try:
        snowflake = SnowflakeClient()
        entity_id = str(uuid.uuid4())
        name_escaped = _escape_sql_string(name)

        if description:
            desc_escaped = _escape_sql_string(description)
            query = f"INSERT INTO entities (entity_id, name, description) VALUES ('{entity_id}', '{name_escaped}', '{desc_escaped}')"
        else:
            query = f"INSERT INTO entities (entity_id, name, description) VALUES ('{entity_id}', '{name_escaped}', NULL)"

        logger.info(f"Executing INSERT query for entity: {name}")
        result = snowflake.execute_query(query)
        logger.info(f"INSERT completed. Result type: {type(result)}")

        # Verify the insert
        verify_query = f"SELECT COUNT(*) as cnt FROM entities WHERE entity_id = '{entity_id}'"
        verify = snowflake.execute_query(verify_query)
        logger.info(f"Verification query result: {verify}")

        logger.info(f"✓ Created entity: {name} (ID: {entity_id})")
        return entity_id
    except Exception as e:
        logger.error(f"Failed to create entity {name}: {e}", exc_info=True)
        raise


def update_entity(entity_id: str, name: str, description: str = None) -> bool:
    """Update an existing entity"""
    try:
        snowflake = SnowflakeClient()
        name_escaped = _escape_sql_string(name)

        if description:
            desc_escaped = _escape_sql_string(description)
            query = f"UPDATE entities SET name = '{name_escaped}', description = '{desc_escaped}', updated_at = CURRENT_TIMESTAMP() WHERE entity_id = '{entity_id}'"
        else:
            query = f"UPDATE entities SET name = '{name_escaped}', description = NULL, updated_at = CURRENT_TIMESTAMP() WHERE entity_id = '{entity_id}'"

        snowflake.execute_query(query)
        logger.info(f"Updated entity: {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update entity {entity_id}: {e}", exc_info=True)
        return False


def delete_entity(entity_id: str) -> bool:
    """Delete an entity and all associated data (cascade)"""
    try:
        snowflake = SnowflakeClient()
        buildings = get_buildings_by_entity(entity_id)

        for building in buildings:
            delete_building(building['BUILDING_ID'])

        query = f"DELETE FROM entities WHERE entity_id = '{entity_id}'"
        snowflake.execute_query(query)
        logger.info(f"Deleted entity: {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete entity {entity_id}: {e}", exc_info=True)
        return False


# ============================================================================
# Building Queries
# ============================================================================

def get_buildings_by_entity(entity_id: str) -> List[Dict[str, Any]]:
    """Get all buildings for an entity"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM buildings WHERE entity_id = '{entity_id}' ORDER BY created_at DESC"
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get buildings for entity {entity_id}: {e}", exc_info=True)
        return []


def get_building_by_id(building_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific building by ID"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM buildings WHERE building_id = '{building_id}'"
        results = snowflake.execute_query(query)
        records = _df_to_records(results)
        return records[0] if records else None
    except Exception as e:
        logger.error(f"Failed to get building {building_id}: {e}", exc_info=True)
        return None


def create_building(entity_id: str, name: str, address: str = None) -> str:
    """Create a new building"""
    try:
        snowflake = SnowflakeClient()
        building_id = str(uuid.uuid4())
        name_escaped = _escape_sql_string(name)

        if address:
            address_escaped = _escape_sql_string(address)
            query = f"INSERT INTO buildings (building_id, entity_id, name, address) VALUES ('{building_id}', '{entity_id}', '{name_escaped}', '{address_escaped}')"
        else:
            query = f"INSERT INTO buildings (building_id, entity_id, name, address) VALUES ('{building_id}', '{entity_id}', '{name_escaped}', NULL)"

        snowflake.execute_query(query)
        logger.info(f"Created building: {name} (ID: {building_id})")
        return building_id
    except Exception as e:
        logger.error(f"Failed to create building {name}: {e}", exc_info=True)
        raise


def update_building(building_id: str, name: str, address: str = None) -> bool:
    """Update an existing building"""
    try:
        snowflake = SnowflakeClient()
        name_escaped = _escape_sql_string(name)

        if address:
            address_escaped = _escape_sql_string(address)
            query = f"UPDATE buildings SET name = '{name_escaped}', address = '{address_escaped}', updated_at = CURRENT_TIMESTAMP() WHERE building_id = '{building_id}'"
        else:
            query = f"UPDATE buildings SET name = '{name_escaped}', address = NULL, updated_at = CURRENT_TIMESTAMP() WHERE building_id = '{building_id}'"

        snowflake.execute_query(query)
        logger.info(f"Updated building: {building_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update building {building_id}: {e}", exc_info=True)
        return False


def delete_building(building_id: str) -> bool:
    """Delete a building and all associated data"""
    try:
        snowflake = SnowflakeClient()

        snowflake.execute_query(f"DELETE FROM budget_items WHERE building_id = '{building_id}'")
        snowflake.execute_query(f"DELETE FROM documents WHERE building_id = '{building_id}'")
        snowflake.execute_query(f"DELETE FROM buildings WHERE building_id = '{building_id}'")

        logger.info(f"Deleted building: {building_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete building {building_id}: {e}", exc_info=True)
        return False


# ============================================================================
# Budget Queries
# ============================================================================

def get_budget_items(building_id: str) -> List[Dict[str, Any]]:
    """Get all budget items for a building"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM budget_items WHERE building_id = '{building_id}' ORDER BY month_year, category"
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get budget items for building {building_id}: {e}", exc_info=True)
        return []


def get_entity_budget(entity_id: str) -> List[Dict[str, Any]]:
    """Get aggregated budget for all buildings in an entity"""
    try:
        snowflake = SnowflakeClient()
        query = f"""
            SELECT
                bi.month_year,
                bi.category,
                SUM(bi.amount) as total_amount
            FROM budget_items bi
            JOIN buildings b ON bi.building_id = b.building_id
            WHERE b.entity_id = '{entity_id}'
            GROUP BY bi.month_year, bi.category
            ORDER BY bi.month_year, bi.category
        """
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get entity budget for {entity_id}: {e}", exc_info=True)
        return []


def upsert_budget_item(building_id: str, month_year: str, category: str, amount: float, notes: str = None) -> bool:
    """Create or update a budget item"""
    try:
        snowflake = SnowflakeClient()
        budget_item_id = str(uuid.uuid4())
        notes_escaped = _escape_sql_string(notes) if notes else 'NULL'

        query = f"""
            MERGE INTO budget_items AS target
            USING (SELECT '{building_id}' AS building_id, '{month_year}' AS month_year, '{category}' AS category) AS source
            ON target.building_id = source.building_id
                AND target.month_year = source.month_year
                AND target.category = source.category
            WHEN MATCHED THEN
                UPDATE SET
                    amount = {amount},
                    notes = '{notes_escaped}',
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (budget_item_id, building_id, month_year, category, amount, notes)
                VALUES ('{budget_item_id}', '{building_id}', '{month_year}', '{category}', {amount}, '{notes_escaped}')
        """

        snowflake.execute_query(query)
        return True
    except Exception as e:
        logger.error(f"Failed to upsert budget item: {e}", exc_info=True)
        return False


def bulk_upsert_budget_items(budget_items: List[Dict[str, Any]]) -> Dict[str, int]:
    """Bulk insert/update budget items"""
    results = {'success': 0, 'failed': 0}

    for item in budget_items:
        try:
            success = upsert_budget_item(
                building_id=item['building_id'],
                month_year=item['month_year'],
                category=item['category'],
                amount=item['amount'],
                notes=item.get('notes')
            )

            if success:
                results['success'] += 1
            else:
                results['failed'] += 1
        except Exception as e:
            logger.error(f"Failed to process budget item: {e}", exc_info=True)
            results['failed'] += 1
            continue

    logger.info(f"Bulk budget upsert: {results['success']} succeeded, {results['failed']} failed")
    return results


# ============================================================================
# Document Queries
# ============================================================================

def get_documents_by_building(building_id: str) -> List[Dict[str, Any]]:
    """Get all documents for a building"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM documents WHERE building_id = '{building_id}' ORDER BY category, uploaded_at DESC"
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get documents for building {building_id}: {e}", exc_info=True)
        return []


def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific document by ID"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM documents WHERE document_id = '{document_id}'"
        results = snowflake.execute_query(query)
        records = _df_to_records(results)
        return records[0] if records else None
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}", exc_info=True)
        return None


def create_document(building_id: str, category: str, filename: str, file_path: str,
                   file_size: int, uploaded_by: str) -> str:
    """Create a new document record"""
    try:
        snowflake = SnowflakeClient()
        document_id = str(uuid.uuid4())
        category_escaped = _escape_sql_string(category)
        filename_escaped = _escape_sql_string(filename)
        filepath_escaped = _escape_sql_string(file_path)
        uploadedby_escaped = _escape_sql_string(uploaded_by)

        query = f"""
            INSERT INTO documents (document_id, building_id, category, filename, file_path, file_size, uploaded_by)
            VALUES ('{document_id}', '{building_id}', '{category_escaped}', '{filename_escaped}', '{filepath_escaped}', {file_size}, '{uploadedby_escaped}')
        """

        snowflake.execute_query(query)
        logger.info(f"Created document: {filename} (ID: {document_id})")
        return document_id
    except Exception as e:
        logger.error(f"Failed to create document {filename}: {e}", exc_info=True)
        raise


def delete_document(document_id: str) -> bool:
    """Delete a document record"""
    try:
        snowflake = SnowflakeClient()
        query = f"DELETE FROM documents WHERE document_id = '{document_id}'"
        snowflake.execute_query(query)
        logger.info(f"Deleted document: {document_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}", exc_info=True)
        return False


# ============================================================================
# Share Token Queries
# ============================================================================

def create_share_token(entity_id: str, expires_days: int = 365) -> str:
    """Generate a shareable token for an entity"""
    try:
        snowflake = SnowflakeClient()
        import secrets
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=expires_days)
        expires_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')

        query = f"INSERT INTO share_tokens (token, entity_id, expires_at) VALUES ('{token}', '{entity_id}', '{expires_str}')"
        snowflake.execute_query(query)
        logger.info(f"Created share token for entity {entity_id}")
        return token
    except Exception as e:
        logger.error(f"Failed to create share token: {e}", exc_info=True)
        raise


def get_entity_by_share_token(token: str) -> Optional[Dict[str, Any]]:
    """Get entity by share token (if valid and not expired)"""
    try:
        snowflake = SnowflakeClient()
        query = f"""
            SELECT e.*
            FROM entities e
            JOIN share_tokens st ON e.entity_id = st.entity_id
            WHERE st.token = '{token}'
              AND (st.expires_at IS NULL OR st.expires_at > CURRENT_TIMESTAMP())
        """
        results = snowflake.execute_query(query)
        records = _df_to_records(results)
        return records[0] if records else None
    except Exception as e:
        logger.error(f"Failed to get entity by share token: {e}", exc_info=True)
        return None


def get_existing_share_token(entity_id: str) -> Optional[str]:
    """Get existing valid share token for an entity"""
    try:
        snowflake = SnowflakeClient()
        query = f"""
            SELECT token
            FROM share_tokens
            WHERE entity_id = '{entity_id}'
              AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP())
            ORDER BY created_at DESC
            LIMIT 1
        """
        results = snowflake.execute_query(query)
        records = _df_to_records(results)
        return records[0]['TOKEN'] if records else None
    except Exception as e:
        logger.error(f"Failed to get existing share token: {e}", exc_info=True)
        return None


def revoke_share_tokens(entity_id: str) -> bool:
    """Revoke all share tokens for an entity"""
    try:
        snowflake = SnowflakeClient()
        query = f"DELETE FROM share_tokens WHERE entity_id = '{entity_id}'"
        snowflake.execute_query(query)
        logger.info(f"Revoked share tokens for entity {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to revoke share tokens: {e}", exc_info=True)
        return False
