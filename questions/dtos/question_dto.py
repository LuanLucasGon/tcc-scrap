from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from questions.entity.questao import Questao


@dataclass
class QuestionDTO:
    """Uma questão como ela é entregue para quem consome o repositório (leituras)."""

    id: str | None
    question_id: str
    subject: str | None
    topics: list[str]
    year: str | None
    exam_board: str | None
    organization: str | None
    exam_title: str | None
    exam_url: str | None
    associated_text: str | None
    enunciation: str | None
    alternatives: dict[str, Any]
    excluido: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: Questao) -> QuestionDTO:
        return cls(
            id=str(entity.id) if entity.id is not None else None,
            question_id=entity.question_id,
            subject=entity.subject,
            topics=list(entity.topics or []),
            year=entity.year,
            exam_board=entity.exam_board,
            organization=entity.organization,
            exam_title=entity.exam_title,
            exam_url=entity.exam_url,
            associated_text=entity.associated_text,
            enunciation=entity.enunciation,
            alternatives=dict(entity.alternatives or {}),
            excluido=bool(entity.excluido),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
