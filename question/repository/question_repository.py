from __future__ import annotations

from dataclasses import asdict

from advanced_alchemy.repository import SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemySyncRepositoryService
from sqlalchemy import select
from sqlalchemy.orm import Session

from question.dtos.question_dto import QuestionDTO
from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.entity.question import Question
from question.repository.question_repository_interface import (
    QuestionRepositoryInterface,
)
from question.repository.upsert_result import UpsertResult
from subject.repository.subject_repository import SubjectRepository
from subject.repository.subject_repository_interface import SubjectRepositoryInterface

MATCH_FIELD = "question_id"


class _QuestionRepository(SQLAlchemySyncRepository[Question]):
    model_type = Question


class QuestionRepository(
    SQLAlchemySyncRepositoryService[Question, _QuestionRepository],
    QuestionRepositoryInterface,
):
    """Persistência de questões sobre o service layer do Advanced Alchemy.

    Recebe a ``Session`` de quem chama; a transação é do chamador. A resolução
    matéria -> FK usa um ``SubjectRepository`` sobre a mesma ``Session`` (injetável
    para testes).
    """

    repository_type = _QuestionRepository

    def __init__(
        self,
        session: Session,
        *,
        subject_repository: SubjectRepositoryInterface | None = None,
        **kwargs: object,
    ) -> None:
        super().__init__(session, **kwargs)
        self._subjects: SubjectRepositoryInterface = (
            subject_repository or SubjectRepository(session=session)
        )

    def upsert_many(self, dtos: list[QuestionScrapedDTO]) -> UpsertResult:
        if not dtos:
            return UpsertResult(inserted=0, updated=0)

        for dto in dtos:
            if not (dto.subject and dto.subject.strip()):
                raise ValueError(f"questão {dto.question_id!r} sem matéria")

        subject_id_by_name = self._subjects.get_or_create_many(
            [dto.subject for dto in dtos]
        )

        rows = []
        for dto in dtos:
            row = asdict(dto)
            row.pop("subject")
            row["subject_id"] = subject_id_by_name[dto.subject]
            rows.append(row)

        incoming_ids = [dto.question_id for dto in dtos]
        existing_ids = self.repository.session.scalars(
            select(Question.question_id).where(Question.question_id.in_(incoming_ids))
        ).all()

        super().upsert_many(rows, match_fields=[MATCH_FIELD], auto_commit=False)

        return UpsertResult.from_ids(incoming_ids, existing_ids)

    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        entity = self.get_one_or_none(question_id=question_id)
        return QuestionDTO.from_entity(entity) if entity is not None else None

    def list_active(self) -> list[QuestionDTO]:
        return [
            QuestionDTO.from_entity(entity)
            for entity in self.get_many(Question.deleted.is_(False))
        ]
