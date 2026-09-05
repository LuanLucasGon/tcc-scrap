from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class QuestionScrapedDTO:
    """Uma questão como o scraper a produz, antes de ser persistida.

    ``subject`` é o nome da matéria exatamente como veio do site; a normalização
    e a resolução para FK acontecem no ``QuestionRepository`` / ``SubjectRepository``.
    """

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
    correct_answer: str | None = None

    @classmethod
    def from_scrape(cls, payload: dict[str, Any]) -> QuestionScrapedDTO:
        """Converte o dicionário cru (já em snake_case) montado pelo scraper em DTO.

        Chaves ausentes usam os defaults do dataclass (``topics``/``alternatives``
        viram lista/dict vazios; os demais campos opcionais viram ``None``).
        """
        return cls(**payload)
