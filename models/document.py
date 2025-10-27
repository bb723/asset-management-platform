"""Document data model"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Document:
    """Document data model representing an uploaded file"""
    document_id: str
    building_id: str
    category: str
    filename: str
    file_path: str
    file_size: int
    uploaded_by: str
    uploaded_at: Optional[datetime] = None

    # Standard document categories
    CATEGORIES = [
        'Insurance Binders',
        'Loan Documents',
        'Management Agreements',
        'HVAC Service Contracts',
        'Lawn Care & Plowing Contracts',
        'Tax Bills',
        'Water/Sewer Bills',
        'Electric Bills',
        'Other'
    ]

    @classmethod
    def from_dict(cls, data: dict) -> 'Document':
        """Create Document instance from dictionary (e.g., from database query)"""
        return cls(
            document_id=data.get('DOCUMENT_ID') or data.get('document_id'),
            building_id=data.get('BUILDING_ID') or data.get('building_id'),
            category=data.get('CATEGORY') or data.get('category'),
            filename=data.get('FILENAME') or data.get('filename'),
            file_path=data.get('FILE_PATH') or data.get('file_path'),
            file_size=data.get('FILE_SIZE') or data.get('file_size') or 0,
            uploaded_by=data.get('UPLOADED_BY') or data.get('uploaded_by'),
            uploaded_at=data.get('UPLOADED_AT') or data.get('uploaded_at')
        )

    def to_dict(self) -> dict:
        """Convert Document instance to dictionary"""
        return {
            'document_id': self.document_id,
            'building_id': self.building_id,
            'category': self.category,
            'filename': self.filename,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'uploaded_by': self.uploaded_by,
            'uploaded_at': self.uploaded_at.isoformat() if isinstance(self.uploaded_at, datetime) else self.uploaded_at
        }

    def get_file_size_display(self) -> str:
        """Get human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

    def __repr__(self) -> str:
        return f"Document(id={self.document_id}, filename={self.filename})"
