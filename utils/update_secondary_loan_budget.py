"""
Utility to update budget with secondary loan debt service
This script adds secondary loan budget items to an existing budget
"""
import sys
import uuid
from datetime import datetime, date
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from foundation.clients import SnowflakeClient


def calculate_amortization(remaining_balance, monthly_rate, monthly_payment):
    """Calculate interest and principal for a specific month"""
    interest_payment = remaining_balance * monthly_rate
    principal_payment = monthly_payment - interest_payment
    new_balance = remaining_balance - principal_payment

    return {
        'interest': interest_payment,
        'principal': principal_payment,
        'remaining_balance': new_balance
    }


def update_secondary_loan_budget(building_id, auto_confirm=False):
    """Add secondary loan budget items to existing budget

    Args:
        building_id: The building to update
        auto_confirm: If True, automatically confirm deletion of existing items
    """
    snowflake = SnowflakeClient()

    # Get building details
    query = f"""
    SELECT
        building_id,
        name,
        secondary_loan_amount,
        secondary_loan_origination_date,
        secondary_loan_duration_years,
        secondary_interest_rate
    FROM buildings
    WHERE building_id = '{building_id}'
    """
    building_result = snowflake.execute_query(query)

    if building_result is None or building_result.empty:
        print(f"Building {building_id} not found")
        return False

    building = building_result.iloc[0]
    building_name = building['NAME']

    # Check if building has a secondary loan
    secondary_amount = float(building['SECONDARY_LOAN_AMOUNT'] or 0)
    if secondary_amount <= 0:
        print(f"Building '{building_name}' has no secondary loan")
        return False

    secondary_rate = float(building['SECONDARY_INTEREST_RATE'] or 0)
    secondary_years = int(building['SECONDARY_LOAN_DURATION_YEARS'] or 0)
    secondary_orig_date = building['SECONDARY_LOAN_ORIGINATION_DATE']

    if secondary_rate <= 0 or secondary_years <= 0:
        print(f"Building '{building_name}' has incomplete secondary loan information")
        return False

    print(f"Processing building: {building_name}")
    print(f"Secondary Loan: ${secondary_amount:,.2f} at {secondary_rate}% for {secondary_years} years")

    # Calculate monthly payment
    monthly_rate = (secondary_rate / 100) / 12
    num_payments = secondary_years * 12
    monthly_payment = secondary_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)

    print(f"Monthly Payment: ${monthly_payment:.2f}")

    # Get existing budget months
    query = f"""
    SELECT DISTINCT month_year
    FROM budget_items
    WHERE building_id = '{building_id}'
    ORDER BY month_year
    """
    months_result = snowflake.execute_query(query)

    if months_result is None or months_result.empty:
        print(f"No existing budget found for building '{building_name}'")
        return False

    months = months_result['MONTH_YEAR'].tolist()
    print(f"Found {len(months)} months in existing budget")

    # Check if secondary loan items already exist
    query = f"""
    SELECT COUNT(*) as count
    FROM budget_items
    WHERE building_id = '{building_id}'
    AND category IN ('Secondary Interest Payment', 'Secondary Principal Payment')
    """
    existing_result = snowflake.execute_query(query)
    existing_count = int(existing_result.iloc[0]['COUNT'])

    if existing_count > 0:
        print(f"Secondary loan budget items already exist ({existing_count} items)")
        if not auto_confirm:
            response = input("Do you want to delete and recreate them? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled")
                return False
        else:
            print("Auto-confirming deletion (called from web UI)")

        # Delete existing secondary loan items
        delete_query = f"""
        DELETE FROM budget_items
        WHERE building_id = '{building_id}'
        AND category IN ('Secondary Interest Payment', 'Secondary Principal Payment')
        """
        snowflake.execute_query(delete_query)
        print("Deleted existing secondary loan items")

    # Calculate loan start position
    if secondary_orig_date:
        if isinstance(secondary_orig_date, str):
            secondary_orig_date = datetime.strptime(secondary_orig_date, '%Y-%m-%d').date()
        elif hasattr(secondary_orig_date, 'date'):
            secondary_orig_date = secondary_orig_date.date()

    # Track remaining balance
    remaining_balance = secondary_amount
    items_created = 0

    # Create budget items for each month
    for i, month in enumerate(months):
        if isinstance(month, str):
            month_date = datetime.strptime(month, '%Y-%m-%d').date()
        elif hasattr(month, 'date'):
            month_date = month.date()
        else:
            month_date = month

        month_str = month_date.strftime('%Y-%m-%d')

        # Check if loan has started
        if secondary_orig_date and month_date < secondary_orig_date:
            # Before loan origination - no payments
            interest_amount = 0
            principal_amount = 0
            note_suffix = "not yet originated"
        else:
            # Calculate amortization
            amortization = calculate_amortization(remaining_balance, monthly_rate, monthly_payment)
            interest_amount = amortization['interest']
            principal_amount = amortization['principal']
            remaining_balance = amortization['remaining_balance']
            note_suffix = f"balance: ${remaining_balance:,.2f}"

        # Insert Secondary Interest Payment
        interest_id = str(uuid.uuid4())
        interest_note = f'Secondary loan: {secondary_rate}% interest - {note_suffix}'
        insert_query = f"""
        INSERT INTO budget_items (
            budget_item_id, building_id, month_year, category, amount, notes, created_at, updated_at
        ) VALUES (
            '{interest_id}',
            '{building_id}',
            '{month_str}',
            'Secondary Interest Payment',
            {interest_amount},
            '{interest_note}',
            CURRENT_TIMESTAMP(),
            CURRENT_TIMESTAMP()
        )
        """
        snowflake.execute_query(insert_query)
        items_created += 1

        # Insert Secondary Principal Payment
        principal_id = str(uuid.uuid4())
        principal_note = f'Secondary loan principal - {note_suffix}'
        insert_query = f"""
        INSERT INTO budget_items (
            budget_item_id, building_id, month_year, category, amount, notes, created_at, updated_at
        ) VALUES (
            '{principal_id}',
            '{building_id}',
            '{month_str}',
            'Secondary Principal Payment',
            {principal_amount},
            '{principal_note}',
            CURRENT_TIMESTAMP(),
            CURRENT_TIMESTAMP()
        )
        """
        snowflake.execute_query(insert_query)
        items_created += 1

    print(f"Successfully created {items_created} secondary loan budget items")
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python update_secondary_loan_budget.py <building_id>")
        print("\nOr run interactively:")
        building_id = input("Enter building ID: ").strip()
    else:
        building_id = sys.argv[1]

    if building_id:
        success = update_secondary_loan_budget(building_id)
        if success:
            print("\nBudget updated successfully!")
            print("The secondary loan payments are now included in the pro-forma.")
        else:
            print("\nFailed to update budget")
    else:
        print("Building ID is required")
