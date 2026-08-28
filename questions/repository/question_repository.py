from __future__ import annotations

from advanced_alchemy.repository import SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemySyncRepositoryService
from sqlalchemy import select

from questions.dtos.question_dto import QuestionDTO
from questions.dtos.question_scraped_dto import QuestionScrapedDTO
from questions.entity.questao import Questao
from questions.repository.question_repository_interface import QuestionRepositoryInterface
from questions.repository.upsert_result import UpsertResult

MATCH_FIELD = "question_id"


class _QuestaoRepository(SQLAlchemySyncRepository[Questao]):
    model_type = Questao


class QuestionRepository(
    SQLAlchemySyncRepositoryService[Questao, _QuestaoRepository],
    QuestionRepositoryInterface,
):
    """Persistência de questões sobre o service layer do Advanced Alchemy.

    O service já traz os métodos de CRUD/consulta prontos (estilo Spring Data) e
    converte o ``QuestionScrapedDTO`` em entidade sozinho — os campos do DTO já
    têm o nome das colunas. Recebe a ``Session`` de quem chama
    (``QuestionRepository(session=session)``); a transação é do chamador.
    """

    repository_type = _QuestaoRepository

    def upsert_many(self, dtos: list[QuestionScrapedDTO]) -> UpsertResult:
        if not dtos:
            return UpsertResult(inserted=0, updated=0)

        incoming_ids = [dto.question_id for dto in dtos]
        existing_ids = self.repository.session.scalars(
            select(Questao.question_id).where(Questao.question_id.in_(incoming_ids))
        ).all()

        super().upsert_many(dtos, match_fields=[MATCH_FIELD], auto_commit=False)

        return UpsertResult.from_ids(incoming_ids, existing_ids)

    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        entity = self.get_one_or_none(question_id=question_id)
        return QuestionDTO.from_entity(entity) if entity is not None else None

    def list_active(self) -> list[QuestionDTO]:
        return [
            QuestionDTO.from_entity(entity)
            for entity in self.get_many(Questao.excluido.is_(False))
        ]
