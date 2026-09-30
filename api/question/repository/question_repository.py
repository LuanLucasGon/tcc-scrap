from __future__ import annotations

from sqlmodel import Session

from question.dtos.question_dto import QuestionDTO
from question.repository.question_repository_interface import (
    QuestionRepositoryInterface,
)


class QuestionRepository(QuestionRepositoryInterface):
    """Leitura de questões via SQLModel.

    A query real (SELECT contra a tabela ``question`` mapeada por
    ``question.entity.question.Question``) entra quando este repositório
    for implementado para valer — esta etapa só fixa a assinatura.
    """

    def __init__(self, session: Session | None) -> None:
        self._session = session

    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        raise NotImplementedError("query real vem em uma etapa futura")
