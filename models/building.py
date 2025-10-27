"""Building data model"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Building:
    """Building data model representing a physical property"""
    building_id: str
    entity_id: str
    name: str
    address: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Building':
        """Create Building instance from dictionary (e.g., from database query)"""
        return cls(
            building_id=data.get('BUILDING_ID') or data.get('building_id'),
            entity_id=data.get('ENTITY_ID') or data.get('entity_id'),
            name=data.get('NAME') or data.get('name'),
            address=data.get('ADDRESS') or data.get('address'),
            created_at=data.get('CREATED_AT') or data.get('created_at'),
            updated_at=data.get('UPDATED_AT') or data.get('updated_at')
        )

    def to_dict(self) -> dict:
        """Convert Building instance to dictionary"""
        return {
            'building_id': self.building_id,
            'entity_id': self.entity_id,
            'name': self.name,
            'address': self.address,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

    def __repr__(self) -> str:
        return f"Building(id={self.building_id}, name={self.name})"
