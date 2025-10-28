"""Database query functions using SnowflakeClient"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from foundation.clients import SnowflakeClient

logger = logging.getLogger(__name__)


# ============================================================================
# Entity Queries
# ============================================================================

def get_all_entities() -> List[Dict[str, Any]]:
    """Get all entities ordered by creation date"""
    try:
        snowflake = SnowflakeClient()
        query = "SELECT * FROM entities ORDER BY created_at DESC"
        results = snowflake.execute_query(query)

        # Convert DataFrame to list of dictionaries
        if results is not None and not results.empty:
            return results.to_dict('records')
        return []
    except Exception as e:
        logger.error(f"Failed to get entities: {e}", exc_info=True)
        return []


def get_entity_by_id(entity_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific entity by ID"""
    try:
        snowflake = SnowflakeClient()
        query = "SELECT * FROM entities WHERE entity_id = %s"
        results = snowflake.execute_query(query, (entity_id,))
        return results[0] if results else None
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}", exc_info=True)
        return None


def create_entity(name: str, description: str = None) -> str:
    """Create a new entity"""
    try:
        snowflake = SnowflakeClient()
        entity_id = str(uuid.uuid4())

        # Escape single quotes in strings
        name_escaped = name.replace("'", "''")
        desc_escaped = description.replace("'", "''") if description else None

        if description:
            query = f"""
                INSERT INTO entities (entity_id, name, description)
                VALUES ('{entity_id}', '{name_escaped}', '{desc_escaped}')
            """
        else:
            query = f"""
                INSERT INTO entities (entity_id, name, description)
                VALUES ('{entity_id}', '{name_escaped}', NULL)
            """

        snowflake.execute_query(query)
        logger.info(f"Created entity: {name} (ID: {entity_id})")
        return entity_id
    except Exception as e:
        logger.error(f"Failed to create entity {name}: {e}", exc_info=True)
        raise


def update_entity(entity_id: str, name: str, description: str = None) -> bool:
    """Update an existing entity"""
    try:
        snowflake = SnowflakeClient()
        query = """
            UPDATE entities
            SET name = %s, description = %s, updated_at = CURRENT_TIMESTAMP()
            WHERE entity_id = %s
        """

        snowflake.execute_query(query, (name, description, entity_id))
        logger.info(f"Updated entity: {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update entity {entity_id}: {e}", exc_info=True)
        return False


def delete_entity(entity_id: str) -> bool:
    """Delete an entity and all associated data (cascade)"""
    try:
        snowflake = SnowflakeClient()

        # Get all buildings for this entity
        buildings = get_buildings_by_entity(entity_id)

        # Delete all data for each building
        for building in buildings:
            delete_building(building['BUILDING_ID'])

        # Delete the entity
        query = "DELETE FROM entities WHERE entity_id = %s"
        snowflake.execute_query(query, (entity_id,))

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
        query = "SELECT * FROM buildings WHERE entity_id = %s ORDER BY created_at DESC"
        results = snowflake.execute_query(query, (entity_id,))
        return results if results else []
    except Exception as e:
        logger.error(f"Failed to get buildings for entity {entity_id}: {e}", exc_info=True)
        return []


def get_building_by_id(building_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific building by ID"""
    try:
        snowflake = SnowflakeClient()
        query = "SELECT * FROM buildings WHERE building_id = %s"
        results = snowflake.execute_query(query, (building_id,))
        return results[0] if results else None
    except Exception as e:
        logger.error(f"Failed to get building {building_id}: {e}", exc_info=True)
        return None


def create_building(entity_id: str, name: str, address: str = None) -> str:
    """Create a new building"""
    try:
        snowflake = SnowflakeClient()
        building_id = str(uuid.uuid4())

        query = """
            INSERT INTO buildings (building_id, entity_id, name, address)
            VALUES (%s, %s, %s, %s)
        """

        snowflake.execute_query(query, (building_id, entity_id, name, address))
        logger.info(f"Created building: {name} (ID: {building_id})")
        return building_id
    except Exception as e:
        logger.error(f"Failed to create building {name}: {e}", exc_info=True)
        raise


def update_building(building_id: str, name: str, address: str = None) -> bool:
    """Update an existing building"""
    try:
        snowflake = SnowflakeClient()
        query = """
            UPDATE buildings
            SET name = %s, address = %s, updated_at = CURRENT_TIMESTAMP()
            WHERE building_id = %s
        """

        snowflake.execute_query(query, (name, address, building_id))
        logger.info(f"Updated building: {building_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update building {building_id}: {e}", exc_info=True)
        return False


def delete_building(building_id: str) -> bool:
    """Delete a building and all associated data"""
    try:
        snowflake = SnowflakeClient()

        # Delete budget items
        snowflake.execute_query("DELETE FROM budget_items WHERE building_id = %s", (building_id,))

        # Delete documents
        snowflake.execute_query("DELETE FROM documents WHERE building_id = %s", (building_id,))

        # Delete the building
        snowflake.execute_query("DELETE FROM buildings WHERE building_id = %s", (building_id,))

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
        query = """
            SELECT * FROM budget_items
            WHERE building_id = %s
            ORDER BY month_year, category
        """
        results = snowflake.execute_query(query, (building_id,))
        return results if results else []
    except Exception as e:
        logger.error(f"Failed to get budget items for building {building_id}: {e}", exc_info=True)
        return []


def get_entity_budget(entity_id: str) -> List[Dict[str, Any]]:
    """Get aggregated budget for all buildings in an entity"""
    try:
        snowflake = SnowflakeClient()
        query = """
            SELECT
                bi.month_year,
                bi.category,
                SUM(bi.amount) as total_amount
            FROM budget_items bi
            JOIN buildings b ON bi.building_id = b.building_id
            WHERE b.entity_id = %s
            GROUP BY bi.month_year, bi.category
            ORDER BY bi.month_year, bi.category
        """
        results = snowflake.execute_query(query, (entity_id,))
        return results if results else []
    except Exception as e:
        logger.error(f"Failed to get entity budget for {entity_id}: {e}", exc_info=True)
        return []


def upsert_budget_item(building_id: str, month_year: str, category: str, amount: float, notes: str = None) -> bool:
    """Create or update a budget item"""
    try:
        snowflake = SnowflakeClient()
        budget_item_id = str(uuid.uuid4())

        query = """
            MERGE INTO budget_items AS target
            USING (SELECT %s AS building_id, %s AS month_year, %s AS category) AS source
            ON target.building_id = source.building_id
                AND target.month_year = source.month_year
                AND target.category = source.category
            WHEN MATCHED THEN
                UPDATE SET
                    amount = %s,
                    notes = %s,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (budget_item_id, building_id, month_year, category, amount, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
        """

        snowflake.execute_query(query, (
            building_id, month_year, category,
            amount, notes,
            budget_item_id, building_id, month_year, category, amount, notes
        ))

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
        query = """
            SELECT * FROM documents
            WHERE building_id = %s
            ORDER BY category, uploaded_at DESC
        """
        results = snowflake.execute_query(query, (building_id,))
        return results if results else []
    except Exception as e:
        logger.error(f"Failed to get documents for building {building_id}: {e}", exc_info=True)
        return []


def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific document by ID"""
    try:
        snowflake = SnowflakeClient()
        query = "SELECT * FROM documents WHERE document_id = %s"
        results = snowflake.execute_query(query, (document_id,))
        return results[0] if results else None
    except Exception as e:
        logger.error(f"Failed to get document {document_id}: {e}", exc_info=True)
        return None


def create_document(building_id: str, category: str, filename: str, file_path: str,
                   file_size: int, uploaded_by: str) -> str:
    """Create a new document record"""
    try:
        snowflake = SnowflakeClient()
        document_id = str(uuid.uuid4())

        query = """
            INSERT INTO documents (document_id, building_id, category, filename,
                                 file_path, file_size, uploaded_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        snowflake.execute_query(query, (
            document_id, building_id, category, filename,
            file_path, file_size, uploaded_by
        ))

        logger.info(f"Created document: {filename} (ID: {document_id})")
        return document_id
    except Exception as e:
        logger.error(f"Failed to create document {filename}: {e}", exc_info=True)
        raise


def delete_document(document_id: str) -> bool:
    """Delete a document record"""
    try:
        snowflake = SnowflakeClient()
        query = "DELETE FROM documents WHERE document_id = %s"
        snowflake.execute_query(query, (document_id,))

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

        # Generate secure token
        import secrets
        token = secrets.token_urlsafe(32)

        expires_at = datetime.now() + timedelta(days=expires_days)

        query = """
            INSERT INTO share_tokens (token, entity_id, expires_at)
            VALUES (%s, %s, %s)
        """

        snowflake.execute_query(query, (token, entity_id, expires_at))
        logger.info(f"Created share token for entity {entity_id}")

        return token
    except Exception as e:
        logger.error(f"Failed to create share token: {e}", exc_info=True)
        raise


def get_entity_by_share_token(token: str) -> Optional[Dict[str, Any]]:
    """Get entity by share token (if valid and not expired)"""
    try:
        snowflake = SnowflakeClient()
        query = """
            SELECT e.*
            FROM entities e
            JOIN share_tokens st ON e.entity_id = st.entity_id
            WHERE st.token = %s
              AND (st.expires_at IS NULL OR st.expires_at > CURRENT_TIMESTAMP())
        """

        results = snowflake.execute_query(query, (token,))
        return results[0] if results else None
    except Exception as e:
        logger.error(f"Failed to get entity by share token: {e}", exc_info=True)
        return None


def get_existing_share_token(entity_id: str) -> Optional[str]:
    """Get existing valid share token for an entity"""
    try:
        snowflake = SnowflakeClient()
        query = """
            SELECT token
            FROM share_tokens
            WHERE entity_id = %s
              AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP())
            ORDER BY created_at DESC
            LIMIT 1
        """

        results = snowflake.execute_query(query, (entity_id,))
        return results[0]['TOKEN'] if results else None
    except Exception as e:
        logger.error(f"Failed to get existing share token: {e}", exc_info=True)
        return None


def revoke_share_tokens(entity_id: str) -> bool:
    """Revoke all share tokens for an entity"""
    try:
        snowflake = SnowflakeClient()
        query = "DELETE FROM share_tokens WHERE entity_id = %s"
        snowflake.execute_query(query, (entity_id,))

        logger.info(f"Revoked share tokens for entity {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to revoke share tokens: {e}", exc_info=True)
        return False
