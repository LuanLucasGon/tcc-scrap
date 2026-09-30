from __future__ import annotations

from question.dtos.question_dto import QuestionDTO
from question.repository.question_repository_interface import (
    QuestionRepositoryInterface,
)


class QuestionService:
    """Orquestra o repositório de questões para os controllers.

    A lógica real entra quando o endpoint for implementado para valer —
    esta etapa só fixa a assinatura.
    """

    def __init__(self, repository: QuestionRepositoryInterface | None) -> None:
        self._repository = repository

    def get_by_question_id(self, question_id: str) -> QuestionDTO | None:
        raise NotImplementedError("lógica real vem em uma etapa futura")
