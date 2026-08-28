from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuestionScrapedDTO:
    """Uma questão como o scraper a produz, antes de ser persistida."""

    question_id: str
    subject: str | None = None
    topics: list[str] = field(default_factory=list)
    year: str | None = None
    exam_board: str | None = None
    organization: str | None = None
    exam_title: str | None = None
    exam_url: str | None = None
    associated_text: str | None = None
    enunciation: str | None = None
    alternatives: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_scrape(cls, payload: dict[str, Any]) -> QuestionScrapedDTO:
        """Converte o dicionário cru montado pelo scraper em um DTO."""
        return cls(
            question_id=payload["questionId"],
            subject=payload.get("subject"),
            topics=payload.get("topics") or [],
            year=payload.get("year"),
            exam_board=payload.get("examBoard"),
            organization=payload.get("organization"),
            exam_title=payload.get("examTitle"),
            exam_url=payload.get("examUrl"),
            associated_text=payload.get("associatedText"),
            enunciation=payload.get("enunciation"),
            alternatives=payload.get("alternatives") or {},
        )
