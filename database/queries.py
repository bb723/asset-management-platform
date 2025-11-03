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


def create_entity(name: str, description: str = None, ein: str = None, accounting_method: str = None) -> str:
    """Create a new entity"""
    try:
        snowflake = SnowflakeClient()
        entity_id = str(uuid.uuid4())
        name_escaped = _escape_sql_string(name)

        # Handle description
        if description:
            desc_escaped = _escape_sql_string(description)
            desc_sql = f"'{desc_escaped}'"
        else:
            desc_sql = 'NULL'

        # Handle EIN
        if ein:
            ein_escaped = _escape_sql_string(ein)
            ein_sql = f"'{ein_escaped}'"
        else:
            ein_sql = 'NULL'

        # Handle accounting method
        if accounting_method:
            accounting_escaped = _escape_sql_string(accounting_method)
            accounting_sql = f"'{accounting_escaped}'"
        else:
            accounting_sql = 'NULL'

        query = f"""
            INSERT INTO entities (entity_id, name, description, ein, accounting_method)
            VALUES ('{entity_id}', '{name_escaped}', {desc_sql}, {ein_sql}, {accounting_sql})
        """

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


def update_entity(entity_id: str, name: str, description: str = None, ein: str = None, accounting_method: str = None) -> bool:
    """Update an existing entity"""
    try:
        snowflake = SnowflakeClient()
        name_escaped = _escape_sql_string(name)

        # Handle description
        if description:
            desc_escaped = _escape_sql_string(description)
            desc_sql = f"'{desc_escaped}'"
        else:
            desc_sql = 'NULL'

        # Handle EIN
        if ein:
            ein_escaped = _escape_sql_string(ein)
            ein_sql = f"'{ein_escaped}'"
        else:
            ein_sql = 'NULL'

        # Handle accounting method
        if accounting_method:
            accounting_escaped = _escape_sql_string(accounting_method)
            accounting_sql = f"'{accounting_escaped}'"
        else:
            accounting_sql = 'NULL'

        query = f"""
            UPDATE entities SET
                name = '{name_escaped}',
                description = {desc_sql},
                ein = {ein_sql},
                accounting_method = {accounting_sql},
                updated_at = CURRENT_TIMESTAMP()
            WHERE entity_id = '{entity_id}'
        """

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


def update_building(building_id: str, name: str, address: str = None,
                   purchase_price: str = None, original_loan_amount: str = None,
                   loan_origination_date: str = None, loan_duration_years: str = None,
                   interest_rate: str = None, additional_principal_paid: str = None,
                   loan_number: str = None, lender: str = None, loan_login_username: str = None,
                   secondary_loan_amount: str = None, secondary_loan_origination_date: str = None,
                   secondary_loan_duration_years: str = None, secondary_interest_rate: str = None,
                   secondary_additional_principal_paid: str = None,
                   secondary_loan_number: str = None, secondary_lender: str = None,
                   secondary_loan_login_username: str = None) -> bool:
    """Update an existing building"""
    try:
        snowflake = SnowflakeClient()
        name_escaped = _escape_sql_string(name)

        # Build the SET clause
        set_parts = [f"name = '{name_escaped}'"]

        # Address
        if address:
            address_escaped = _escape_sql_string(address)
            set_parts.append(f"address = '{address_escaped}'")
        else:
            set_parts.append("address = NULL")

        # Debt fields
        if purchase_price:
            set_parts.append(f"purchase_price = {purchase_price}")
        else:
            set_parts.append("purchase_price = NULL")

        if original_loan_amount:
            set_parts.append(f"original_loan_amount = {original_loan_amount}")
        else:
            set_parts.append("original_loan_amount = NULL")

        if loan_origination_date:
            set_parts.append(f"loan_origination_date = '{loan_origination_date}'")
        else:
            set_parts.append("loan_origination_date = NULL")

        if loan_duration_years:
            set_parts.append(f"loan_duration_years = {loan_duration_years}")
        else:
            set_parts.append("loan_duration_years = NULL")

        if interest_rate:
            set_parts.append(f"interest_rate = {interest_rate}")
        else:
            set_parts.append("interest_rate = NULL")

        if additional_principal_paid:
            set_parts.append(f"additional_principal_paid = {additional_principal_paid}")
        else:
            set_parts.append("additional_principal_paid = NULL")

        # Primary loan reference fields
        if loan_number:
            loan_number_escaped = _escape_sql_string(loan_number)
            set_parts.append(f"loan_number = '{loan_number_escaped}'")
        else:
            set_parts.append("loan_number = NULL")

        if lender:
            lender_escaped = _escape_sql_string(lender)
            set_parts.append(f"lender = '{lender_escaped}'")
        else:
            set_parts.append("lender = NULL")

        if loan_login_username:
            loan_login_username_escaped = _escape_sql_string(loan_login_username)
            set_parts.append(f"loan_login_username = '{loan_login_username_escaped}'")
        else:
            set_parts.append("loan_login_username = NULL")

        # Secondary loan fields
        if secondary_loan_amount:
            set_parts.append(f"secondary_loan_amount = {secondary_loan_amount}")
        else:
            set_parts.append("secondary_loan_amount = NULL")

        if secondary_loan_origination_date:
            set_parts.append(f"secondary_loan_origination_date = '{secondary_loan_origination_date}'")
        else:
            set_parts.append("secondary_loan_origination_date = NULL")

        if secondary_loan_duration_years:
            set_parts.append(f"secondary_loan_duration_years = {secondary_loan_duration_years}")
        else:
            set_parts.append("secondary_loan_duration_years = NULL")

        if secondary_interest_rate:
            set_parts.append(f"secondary_interest_rate = {secondary_interest_rate}")
        else:
            set_parts.append("secondary_interest_rate = NULL")

        if secondary_additional_principal_paid:
            set_parts.append(f"secondary_additional_principal_paid = {secondary_additional_principal_paid}")
        else:
            set_parts.append("secondary_additional_principal_paid = NULL")

        # Secondary loan reference fields
        if secondary_loan_number:
            secondary_loan_number_escaped = _escape_sql_string(secondary_loan_number)
            set_parts.append(f"secondary_loan_number = '{secondary_loan_number_escaped}'")
        else:
            set_parts.append("secondary_loan_number = NULL")

        if secondary_lender:
            secondary_lender_escaped = _escape_sql_string(secondary_lender)
            set_parts.append(f"secondary_lender = '{secondary_lender_escaped}'")
        else:
            set_parts.append("secondary_lender = NULL")

        if secondary_loan_login_username:
            secondary_loan_login_username_escaped = _escape_sql_string(secondary_loan_login_username)
            set_parts.append(f"secondary_loan_login_username = '{secondary_loan_login_username_escaped}'")
        else:
            set_parts.append("secondary_loan_login_username = NULL")

        set_parts.append("updated_at = CURRENT_TIMESTAMP()")

        set_clause = ", ".join(set_parts)
        query = f"UPDATE buildings SET {set_clause} WHERE building_id = '{building_id}'"

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


def get_building_financial_metrics(building_id: str) -> Dict[str, Any]:
    """Get financial metrics for a building (annual NOI, cashflow, etc.)"""
    try:
        snowflake = SnowflakeClient()
        # Get only the next 12 months starting from current month
        query = f"""
            SELECT
                category,
                SUM(amount) as annual_amount
            FROM budget_items
            WHERE building_id = '{building_id}'
                AND category IN ('Net Operating Income', 'Cashflow', 'Revenue')
                AND month_year >= DATE_TRUNC('MONTH', CURRENT_DATE())
                AND month_year < DATEADD('MONTH', 12, DATE_TRUNC('MONTH', CURRENT_DATE()))
            GROUP BY category
        """
        results = snowflake.execute_query(query)
        records = _df_to_records(results)

        metrics = {
            'annual_noi': 0,
            'annual_cashflow': 0,
            'annual_revenue': 0,
            'estimated_value': 0
        }

        for record in records:
            category = record.get('CATEGORY', '')
            amount = float(record.get('ANNUAL_AMOUNT', 0))

            if category == 'Net Operating Income':
                metrics['annual_noi'] = amount
                # Calculate estimated value at 8.5% cap rate
                if amount > 0:
                    metrics['estimated_value'] = amount / 0.085
            elif category == 'Cashflow':
                metrics['annual_cashflow'] = amount
            elif category == 'Revenue':
                metrics['annual_revenue'] = amount

        return metrics
    except Exception as e:
        logger.error(f"Failed to get financial metrics for building {building_id}: {e}", exc_info=True)
        return {
            'annual_noi': 0,
            'annual_cashflow': 0,
            'annual_revenue': 0,
            'estimated_value': 0
        }


def _calculate_amortization_principal_paid(principal: float, annual_rate: float,
                                           duration_years: int, months_elapsed: int) -> float:
    """Calculate total principal paid using amortization formula"""
    if principal <= 0 or annual_rate <= 0 or duration_years <= 0 or months_elapsed <= 0:
        return 0

    # Monthly interest rate
    monthly_rate = annual_rate / 100 / 12
    total_payments = duration_years * 12

    # Calculate monthly payment using amortization formula
    # M = P * [r(1+r)^n] / [(1+r)^n - 1]
    if monthly_rate == 0:
        monthly_payment = principal / total_payments
    else:
        monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** total_payments) / \
                         ((1 + monthly_rate) ** total_payments - 1)

    # Calculate total principal paid over months_elapsed
    balance = principal
    total_principal_paid = 0

    for month in range(min(months_elapsed, total_payments)):
        interest_payment = balance * monthly_rate
        principal_payment = monthly_payment - interest_payment
        total_principal_paid += principal_payment
        balance -= principal_payment

        if balance <= 0:
            break

    return total_principal_paid


def get_building_current_debt(building_id: str) -> Dict[str, Any]:
    """Calculate current debt position for a building"""
    try:
        snowflake = SnowflakeClient()
        from datetime import datetime
        from dateutil.relativedelta import relativedelta

        # First, get building debt information from the buildings table (both primary and secondary loans)
        building_query = f"""
            SELECT
                original_loan_amount,
                loan_origination_date,
                loan_duration_years,
                interest_rate,
                additional_principal_paid,
                secondary_loan_amount,
                secondary_loan_origination_date,
                secondary_loan_duration_years,
                secondary_interest_rate,
                secondary_additional_principal_paid
            FROM buildings
            WHERE building_id = '{building_id}'
        """
        building_results = snowflake.execute_query(building_query)
        building_records = _df_to_records(building_results)

        original_loan = 0
        loan_origination_date = None
        loan_duration_years = None
        interest_rate = None
        additional_principal_paid = 0

        secondary_loan = 0
        secondary_loan_origination_date = None
        secondary_loan_duration_years = None
        secondary_interest_rate = None
        secondary_additional_principal_paid = 0

        if building_records and len(building_records) > 0:
            building_data = building_records[0]
            original_loan_val = building_data.get('ORIGINAL_LOAN_AMOUNT')
            if original_loan_val:
                original_loan = float(original_loan_val)

            # Get loan origination date
            loan_orig_val = building_data.get('LOAN_ORIGINATION_DATE')
            if loan_orig_val:
                from datetime import date as date_type
                if isinstance(loan_orig_val, date_type):
                    # Already a datetime.date object
                    loan_origination_date = loan_orig_val
                elif isinstance(loan_orig_val, str):
                    try:
                        loan_origination_date = datetime.strptime(loan_orig_val, '%Y-%m-%d').date()
                    except:
                        pass
                elif hasattr(loan_orig_val, 'date'):
                    # datetime.datetime object
                    loan_origination_date = loan_orig_val.date()

            # Get loan duration and interest rate
            loan_duration_years = building_data.get('LOAN_DURATION_YEARS')
            interest_rate_val = building_data.get('INTEREST_RATE')
            if interest_rate_val:
                interest_rate = float(interest_rate_val)

            # Get additional principal paid
            additional_principal_val = building_data.get('ADDITIONAL_PRINCIPAL_PAID')
            if additional_principal_val:
                additional_principal_paid = float(additional_principal_val)

            # Get secondary loan information
            secondary_loan_val = building_data.get('SECONDARY_LOAN_AMOUNT')
            if secondary_loan_val:
                secondary_loan = float(secondary_loan_val)

            # Get secondary loan origination date
            secondary_loan_orig_val = building_data.get('SECONDARY_LOAN_ORIGINATION_DATE')
            if secondary_loan_orig_val:
                from datetime import date as date_type
                if isinstance(secondary_loan_orig_val, date_type):
                    secondary_loan_origination_date = secondary_loan_orig_val
                elif isinstance(secondary_loan_orig_val, str):
                    try:
                        secondary_loan_origination_date = datetime.strptime(secondary_loan_orig_val, '%Y-%m-%d').date()
                    except:
                        pass
                elif hasattr(secondary_loan_orig_val, 'date'):
                    secondary_loan_origination_date = secondary_loan_orig_val.date()

            # Get secondary loan duration and interest rate
            secondary_loan_duration_years = building_data.get('SECONDARY_LOAN_DURATION_YEARS')
            secondary_interest_rate_val = building_data.get('SECONDARY_INTEREST_RATE')
            if secondary_interest_rate_val:
                secondary_interest_rate = float(secondary_interest_rate_val)

            # Get secondary additional principal paid
            secondary_additional_principal_val = building_data.get('SECONDARY_ADDITIONAL_PRINCIPAL_PAID')
            if secondary_additional_principal_val:
                secondary_additional_principal_paid = float(secondary_additional_principal_val)

        # If no building debt info, try to extract from budget items
        if original_loan == 0:
            query = f"""
                SELECT
                    month_year,
                    amount,
                    notes
                FROM budget_items
                WHERE building_id = '{building_id}'
                    AND category = 'Principal Payment'
                ORDER BY month_year ASC
            """
            results = snowflake.execute_query(query)
            records = _df_to_records(results)

            if records:
                # Extract original loan from first payment's notes
                first_record = records[0]
                notes = first_record.get('NOTES', '')
                if notes and 'balance:' in notes.lower():
                    try:
                        balance_str = notes.lower().split('balance:')[1].strip()
                        balance_str = balance_str.replace('$', '').replace(',', '').split()[0]
                        remaining_after_first = float(balance_str)
                        first_payment = float(first_record.get('AMOUNT', 0))
                        original_loan = remaining_after_first + first_payment
                    except:
                        pass

        # Calculate current debt (primary + secondary)
        current_date = datetime.now().date()

        # Calculate primary loan debt
        primary_principal_paid = 0
        primary_current_debt = original_loan

        # If we have complete primary loan info, calculate using amortization
        if original_loan > 0 and loan_origination_date and loan_duration_years and interest_rate:
            # Calculate months elapsed since loan origination
            months_elapsed = (current_date.year - loan_origination_date.year) * 12 + \
                           (current_date.month - loan_origination_date.month)

            if months_elapsed > 0:
                primary_principal_paid = _calculate_amortization_principal_paid(
                    original_loan, interest_rate, loan_duration_years, months_elapsed
                )
                # Add any additional principal payments made
                primary_principal_paid += additional_principal_paid
                primary_current_debt = original_loan - primary_principal_paid
                primary_current_debt = max(0, primary_current_debt)

        # Calculate secondary loan debt
        secondary_principal_paid = 0
        secondary_current_debt = secondary_loan

        # If we have complete secondary loan info, calculate using amortization
        if secondary_loan > 0 and secondary_loan_origination_date and secondary_loan_duration_years and secondary_interest_rate:
            # Calculate months elapsed since secondary loan origination
            secondary_months_elapsed = (current_date.year - secondary_loan_origination_date.year) * 12 + \
                                      (current_date.month - secondary_loan_origination_date.month)

            if secondary_months_elapsed > 0:
                secondary_principal_paid = _calculate_amortization_principal_paid(
                    secondary_loan, secondary_interest_rate, secondary_loan_duration_years, secondary_months_elapsed
                )
                # Add any additional principal payments made on secondary loan
                secondary_principal_paid += secondary_additional_principal_paid
                secondary_current_debt = secondary_loan - secondary_principal_paid
                secondary_current_debt = max(0, secondary_current_debt)

        # Total debt is primary + secondary
        total_principal_paid = primary_principal_paid + secondary_principal_paid
        current_debt = primary_current_debt + secondary_current_debt
        total_original_loan = original_loan + secondary_loan

        return {
            'original_loan': total_original_loan,  # Total of both loans
            'current_debt': current_debt,  # Combined current debt
            'total_principal_paid': total_principal_paid,  # Combined principal paid
            'loan_origination_date': loan_origination_date,  # Primary loan origination date
            'primary_loan': original_loan,
            'primary_current_debt': primary_current_debt,
            'secondary_loan': secondary_loan,
            'secondary_current_debt': secondary_current_debt
        }

    except Exception as e:
        logger.error(f"Failed to calculate current debt for building {building_id}: {e}", exc_info=True)
        return {
            'original_loan': 0,
            'current_debt': 0,
            'total_principal_paid': 0,
            'loan_origination_date': None,
            'primary_loan': 0,
            'primary_current_debt': 0,
            'secondary_loan': 0,
            'secondary_current_debt': 0
        }


def get_entity_financial_metrics(entity_id: str) -> Dict[str, Any]:
    """Get aggregated financial metrics for an entity (all buildings combined)"""
    try:
        snowflake = SnowflakeClient()

        # Get all buildings for this entity
        buildings = get_buildings_by_entity(entity_id)

        metrics = {
            'total_value': 0,
            'total_debt': 0,
            'total_equity': 0,
            'annual_cashflow': 0,
            'annual_noi': 0,
            'building_count': len(buildings)
        }

        # Sum up metrics from all buildings
        for building in buildings:
            building_id = building.get('BUILDING_ID')

            # Get financial metrics
            building_metrics = get_building_financial_metrics(building_id)
            metrics['total_value'] += building_metrics.get('estimated_value', 0)
            metrics['annual_cashflow'] += building_metrics.get('annual_cashflow', 0)
            metrics['annual_noi'] += building_metrics.get('annual_noi', 0)

            # Get debt position
            debt_info = get_building_current_debt(building_id)
            metrics['total_debt'] += debt_info.get('current_debt', 0)

        # Calculate equity
        metrics['total_equity'] = metrics['total_value'] - metrics['total_debt']

        return metrics

    except Exception as e:
        logger.error(f"Failed to get entity financial metrics for {entity_id}: {e}", exc_info=True)
        return {
            'total_value': 0,
            'total_debt': 0,
            'total_equity': 0,
            'annual_cashflow': 0,
            'annual_noi': 0,
            'building_count': 0
        }


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


def get_entity_budget_with_buildings(entity_id: str) -> Dict[str, Any]:
    """Get aggregated budget for entity with drill-down by building"""
    try:
        snowflake = SnowflakeClient()
        query = f"""
            SELECT
                b.building_id,
                b.name as building_name,
                bi.month_year,
                bi.category,
                SUM(bi.amount) as amount
            FROM budget_items bi
            JOIN buildings b ON bi.building_id = b.building_id
            WHERE b.entity_id = '{entity_id}'
            GROUP BY b.building_id, b.name, bi.month_year, bi.category
            ORDER BY b.name, bi.month_year, bi.category
        """
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get entity budget with buildings for {entity_id}: {e}", exc_info=True)
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
    """Bulk insert/update budget items using optimized batch processing"""
    results = {'success': 0, 'failed': 0}

    if not budget_items:
        return results

    try:
        snowflake = SnowflakeClient()

        # Build VALUES clauses for the source table
        source_values = []
        for item in budget_items:
            budget_item_id = str(uuid.uuid4())
            building_id = item['building_id']
            month_year = item['month_year']
            category = item['category']
            amount = float(item['amount'])
            notes = _escape_sql_string(item.get('notes', ''))

            # Use NULL for empty notes, otherwise wrap in quotes
            notes_value = 'NULL' if not notes or notes == 'NULL' else f"'{notes}'"

            source_values.append(
                f"('{budget_item_id}', '{building_id}', '{month_year}', '{category}', {amount}, {notes_value})"
            )

        # Create the MERGE query with all values at once
        values_clause = ',\n                '.join(source_values)

        query = f"""
            MERGE INTO budget_items AS target
            USING (
                SELECT * FROM VALUES
                {values_clause}
            ) AS source(budget_item_id, building_id, month_year, category, amount, notes)
            ON target.building_id = source.building_id
                AND target.month_year = source.month_year
                AND target.category = source.category
            WHEN MATCHED THEN
                UPDATE SET
                    amount = source.amount,
                    notes = source.notes,
                    updated_at = CURRENT_TIMESTAMP()
            WHEN NOT MATCHED THEN
                INSERT (budget_item_id, building_id, month_year, category, amount, notes, created_at, updated_at)
                VALUES (source.budget_item_id, source.building_id, source.month_year, source.category,
                        source.amount, source.notes, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
        """

        logger.info(f"Executing bulk upsert for {len(budget_items)} budget items")
        snowflake.execute_query(query)
        results['success'] = len(budget_items)
        logger.info(f"Bulk budget upsert completed: {results['success']} items processed")

    except Exception as e:
        logger.error(f"Failed to bulk upsert budget items: {e}", exc_info=True)
        logger.error(f"Query that failed: {query if 'query' in locals() else 'Query not constructed'}")
        results['failed'] = len(budget_items)

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
                   file_size: int, uploaded_by: str, effective_date: str = None, end_date: str = None) -> str:
    """Create a new document record"""
    try:
        snowflake = SnowflakeClient()
        document_id = str(uuid.uuid4())
        category_escaped = _escape_sql_string(category)
        filename_escaped = _escape_sql_string(filename)
        filepath_escaped = _escape_sql_string(file_path)
        uploadedby_escaped = _escape_sql_string(uploaded_by)

        # Handle dates
        if effective_date:
            effective_date_sql = f"'{effective_date}'"
        else:
            effective_date_sql = 'NULL'

        if end_date:
            end_date_sql = f"'{end_date}'"
        else:
            end_date_sql = 'NULL'

        query = f"""
            INSERT INTO documents (document_id, building_id, category, filename, file_path, file_size, uploaded_by, effective_date, end_date)
            VALUES ('{document_id}', '{building_id}', '{category_escaped}', '{filename_escaped}', '{filepath_escaped}', {file_size}, '{uploadedby_escaped}', {effective_date_sql}, {end_date_sql})
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


# ============================================================================
# Apartment Queries
# ============================================================================

def get_apartments_by_building(building_id: str) -> List[Dict[str, Any]]:
    """Get all apartments for a building"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM apartments WHERE building_id = '{building_id}' ORDER BY unit_number"
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get apartments for building {building_id}: {e}", exc_info=True)
        return []


def create_apartment(building_id: str, unit_number: str, monthly_rent: float) -> str:
    """Create a new apartment"""
    try:
        snowflake = SnowflakeClient()
        apartment_id = str(uuid.uuid4())
        unit_escaped = _escape_sql_string(unit_number)

        query = f"""
            INSERT INTO apartments (apartment_id, building_id, unit_number, monthly_rent)
            VALUES ('{apartment_id}', '{building_id}', '{unit_escaped}', {monthly_rent})
        """

        snowflake.execute_query(query)
        logger.info(f"Created apartment: {unit_number} (ID: {apartment_id})")
        return apartment_id
    except Exception as e:
        logger.error(f"Failed to create apartment {unit_number}: {e}", exc_info=True)
        raise


def update_apartment(apartment_id: str, unit_number: str, monthly_rent: float) -> bool:
    """Update an existing apartment"""
    try:
        snowflake = SnowflakeClient()
        unit_escaped = _escape_sql_string(unit_number)

        query = f"""
            UPDATE apartments
            SET unit_number = '{unit_escaped}',
                monthly_rent = {monthly_rent},
                updated_at = CURRENT_TIMESTAMP()
            WHERE apartment_id = '{apartment_id}'
        """

        snowflake.execute_query(query)
        logger.info(f"Updated apartment: {apartment_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update apartment {apartment_id}: {e}", exc_info=True)
        return False


def delete_apartment(apartment_id: str) -> bool:
    """Delete an apartment"""
    try:
        snowflake = SnowflakeClient()
        query = f"DELETE FROM apartments WHERE apartment_id = '{apartment_id}'"
        snowflake.execute_query(query)
        logger.info(f"Deleted apartment: {apartment_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete apartment {apartment_id}: {e}", exc_info=True)
        return False


# ============================================================================
# Entity Document Queries
# ============================================================================

def get_entity_documents(entity_id: str) -> List[Dict[str, Any]]:
    """Get all documents for an entity"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM entity_documents WHERE entity_id = '{entity_id}' ORDER BY uploaded_at DESC"
        results = snowflake.execute_query(query)
        return _df_to_records(results)
    except Exception as e:
        logger.error(f"Failed to get documents for entity {entity_id}: {e}", exc_info=True)
        return []


def create_entity_document(entity_id: str, category: str, filename: str, file_path: str, file_size: int, uploaded_by: str) -> str:
    """Create a new entity document record"""
    try:
        snowflake = SnowflakeClient()
        document_id = str(uuid.uuid4())
        category_escaped = _escape_sql_string(category)
        filename_escaped = _escape_sql_string(filename)
        filepath_escaped = _escape_sql_string(file_path)
        uploadedby_escaped = _escape_sql_string(uploaded_by)

        query = f"""
            INSERT INTO entity_documents (document_id, entity_id, category, filename, file_path, file_size, uploaded_by)
            VALUES ('{document_id}', '{entity_id}', '{category_escaped}', '{filename_escaped}', '{filepath_escaped}', {file_size}, '{uploadedby_escaped}')
        """

        snowflake.execute_query(query)
        logger.info(f"Created entity document: {filename} (ID: {document_id})")
        return document_id
    except Exception as e:
        logger.error(f"Failed to create entity document {filename}: {e}", exc_info=True)
        raise


def delete_entity_document(document_id: str) -> bool:
    """Delete an entity document record"""
    try:
        snowflake = SnowflakeClient()
        query = f"DELETE FROM entity_documents WHERE document_id = '{document_id}'"
        snowflake.execute_query(query)
        logger.info(f"Deleted entity document: {document_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete entity document {document_id}: {e}", exc_info=True)
        return False


def get_entity_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific entity document by ID"""
    try:
        snowflake = SnowflakeClient()
        query = f"SELECT * FROM entity_documents WHERE document_id = '{document_id}'"
        results = snowflake.execute_query(query)
        records = _df_to_records(results)
        return records[0] if records else None
    except Exception as e:
        logger.error(f"Failed to get entity document {document_id}: {e}", exc_info=True)
        return None
