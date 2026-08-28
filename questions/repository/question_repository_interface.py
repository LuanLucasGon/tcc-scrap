from __future__ import annotations

from abc import ABC, abstractmethod

from questions.dtos.question_dto import QuestionDTO
from questions.dtos.question_scraped_dto import QuestionScrapedDTO
from questions.repository.upsert_result import UpsertResult


class QuestionRepositoryInterface(ABC):
    """Porta de persistência para questões (estilo Spring Data repository)."""

    @abstractmethod
    def upsert_many(self, dtos: list[QuestionScrapedDTO]) -> UpsertResult:
        """Insere ou atualiza questões usando ``question_id`` como chave de conflito."""

    @abstractmethod
    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        """Retorna a questão pelo ``question_id`` do site, ou ``None``."""

    @abstractmethod
    def list_active(self) -> list[QuestionDTO]:
        """Lista as questões não excluídas (``excluido = false``)."""
