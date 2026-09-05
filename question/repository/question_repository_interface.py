from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from question.dtos.question_dto import QuestionDTO
from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.repository.upsert_result import UpsertResult


class QuestionRepositoryInterface(ABC):
    """Porta de persistência para questões (estilo Spring Data repository)."""

    @abstractmethod
    def upsert_many(
        self, dtos: list[QuestionScrapedDTO], subject_id_by_name: dict[str, UUID]
    ) -> UpsertResult:
        """Insere ou atualiza questões usando ``question_id`` como chave de conflito.

        ``subject_id_by_name`` já deve trazer o ``subject_id`` resolvido para
        cada ``dto.subject`` (nome cru) — resolver a matéria não é
        responsabilidade deste repositório.
        """

    @abstractmethod
    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        """Retorna a questão pelo ``question_id`` do site, ou ``None``."""

    @abstractmethod
    def list_active(self) -> list[QuestionDTO]:
        """Lista as questões não excluídas (``deleted = false``)."""
