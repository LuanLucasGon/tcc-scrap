from __future__ import annotations

from abc import ABC, abstractmethod

from question.dtos.question_dto import QuestionDTO


class QuestionRepositoryInterface(ABC):
    """Porta de leitura de questões para a API (estilo Spring Data)."""

    @abstractmethod
    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        """Retorna a questão pelo ``question_id`` do site, ou ``None``."""
