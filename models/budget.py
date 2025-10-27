"""Budget data model"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


@dataclass
class BudgetItem:
    """Budget item data model representing a single budget entry"""
    budget_item_id: str
    building_id: str
    month_year: date
    category: str
    amount: Decimal
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Standard budget categories
    CATEGORIES = [
        'Revenue',
        'Operating Expenses',
        'Debt Service',
        'Capital Expenses',
        'Net Operating Income'
    ]

    @classmethod
    def from_dict(cls, data: dict) -> 'BudgetItem':
        """Create BudgetItem instance from dictionary (e.g., from database query)"""
        month_year_val = data.get('MONTH_YEAR') or data.get('month_year')
        if isinstance(month_year_val, str):
            month_year_val = datetime.strptime(month_year_val, '%Y-%m-%d').date()

        amount_val = data.get('AMOUNT') or data.get('amount') or 0
        if not isinstance(amount_val, Decimal):
            amount_val = Decimal(str(amount_val))

        return cls(
            budget_item_id=data.get('BUDGET_ITEM_ID') or data.get('budget_item_id'),
            building_id=data.get('BUILDING_ID') or data.get('building_id'),
            month_year=month_year_val,
            category=data.get('CATEGORY') or data.get('category'),
            amount=amount_val,
            notes=data.get('NOTES') or data.get('notes'),
            created_at=data.get('CREATED_AT') or data.get('created_at'),
            updated_at=data.get('UPDATED_AT') or data.get('updated_at')
        )

    def to_dict(self) -> dict:
        """Convert BudgetItem instance to dictionary"""
        return {
            'budget_item_id': self.budget_item_id,
            'building_id': self.building_id,
            'month_year': self.month_year.isoformat() if isinstance(self.month_year, date) else self.month_year,
            'category': self.category,
            'amount': float(self.amount),
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

    def __repr__(self) -> str:
        return f"BudgetItem(building={self.building_id}, month={self.month_year}, category={self.category}, amount=${self.amount})"
