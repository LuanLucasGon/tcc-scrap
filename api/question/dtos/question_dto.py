from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class QuestionDTO:
    """Uma questão como será entregue por quem consome a API (leitura).

    A conversão a partir de ``question.entity.question.Question`` entra
    quando o repositório for implementado de verdade.
    """

    id: str
    question_id: str
    subject_id: str
    topics: list[str]
    year: str | None
    exam_board: str | None
    organization: str | None
    exam_title: str | None
    exam_url: str | None
    associated_text: str | None
    enunciation: str | None
    alternatives: dict[str, Any]
    correct_answer: str | None
    deleted: bool
    created_at: datetime
    updated_at: datetime
