from __future__ import annotations

from fastapi import APIRouter

from question.dtos.question_dto import QuestionDTO
from question.service.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["question"])


@router.get("/{question_id}")
async def get_question_by_id(question_id: str) -> QuestionDTO | None:
    """Referência de endpoint — implementação real vem em etapa futura.

    Este router não é incluído em ``app.main.app`` ainda: só existe para
    fixar a assinatura da camada de controller.
    """
    service = QuestionService(repository=None)
    return service.get_by_question_id(question_id)
