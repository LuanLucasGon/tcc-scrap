from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from question.entity.question import Question


@dataclass
class QuestionDTO:
    """Uma questão como ela é entregue para quem consome o repositório (leituras)."""

    id: str | None
    question_id: str
    subject_id: str | None
    subject_name: str | None
    topics: list[str]
    year: str | None
    exam_board: str | None
    organization: str | None
    exam_title: str | None
    exam_url: str | None
    associated_text: str | None
    enunciation: str | None
    alternatives: dict[str, Any]
    deleted: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: Question) -> QuestionDTO:
        return cls(
            id=str(entity.id) if entity.id is not None else None,
            question_id=entity.question_id,
            subject_id=(
                str(entity.subject_id) if entity.subject_id is not None else None
            ),
            subject_name=entity.subject.name if entity.subject is not None else None,
            topics=list(entity.topics or []),
            year=entity.year,
            exam_board=entity.exam_board,
            organization=entity.organization,
            exam_title=entity.exam_title,
            exam_url=entity.exam_url,
            associated_text=entity.associated_text,
            enunciation=entity.enunciation,
            alternatives=dict(entity.alternatives or {}),
            deleted=bool(entity.deleted),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
