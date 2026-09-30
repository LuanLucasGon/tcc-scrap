from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from subject.entity.subject import Subject


@dataclass
class SubjectDTO:
    """Uma matéria como ela é entregue para quem consome o repositório (leituras)."""

    id: str
    name: str
    active: bool
    deleted: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: Subject) -> SubjectDTO:
        return cls(
            id=str(entity.id),
            name=entity.name,
            active=bool(entity.active),
            deleted=bool(entity.deleted),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
