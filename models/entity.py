"""Entity data model"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Entity:
    """Entity data model representing a property management entity"""
    entity_id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> 'Entity':
        """Create Entity instance from dictionary (e.g., from database query)"""
        return cls(
            entity_id=data.get('ENTITY_ID') or data.get('entity_id'),
            name=data.get('NAME') or data.get('name'),
            description=data.get('DESCRIPTION') or data.get('description'),
            created_at=data.get('CREATED_AT') or data.get('created_at'),
            updated_at=data.get('UPDATED_AT') or data.get('updated_at')
        )

    def to_dict(self) -> dict:
        """Convert Entity instance to dictionary"""
        return {
            'entity_id': self.entity_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            'updated_at': self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at
        }

    def __repr__(self) -> str:
        return f"Entity(id={self.entity_id}, name={self.name})"
