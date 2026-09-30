from __future__ import annotations

from uuid import UUID

from advanced_alchemy.repository import SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemySyncRepositoryService
from sqlalchemy import tuple_

from questionfile.dtos.question_file_dto import QuestionFileDTO
from questionfile.entity.question_file import QuestionFile
from questionfile.repository.question_file_repository_interface import (
    QuestionFileRepositoryInterface,
)


class _QuestionFileRepository(SQLAlchemySyncRepository[QuestionFile]):
    model_type = QuestionFile


class QuestionFileRepository(
    SQLAlchemySyncRepositoryService[QuestionFile, _QuestionFileRepository],
    QuestionFileRepositoryInterface,
):
    """Persistência de arquivos de questão sobre o service layer do Advanced Alchemy.

    Recebe a ``Session`` de quem chama; a transação é do chamador. Não baixa
    nada da rede — isso é responsabilidade de quem orquestra (``main.py``).
    """

    repository_type = _QuestionFileRepository

    def get_ids_by_pairs(
        self, pairs: list[tuple[str, str]]
    ) -> dict[tuple[str, str], UUID]:
        if not pairs:
            return {}
        rows = self.get_many(
            tuple_(QuestionFile.question_number_id, QuestionFile.url).in_(pairs)
        )
        return {(row.question_number_id, row.url): row.id for row in rows}

    def get_contents_by_urls(self, urls: list[str]) -> dict[str, bytes]:
        if not urls:
            return {}
        contents: dict[str, bytes] = {}
        for row in self.get_many(QuestionFile.url.in_(urls)):
            contents.setdefault(row.url, row.content)
        return contents

    def create_missing(
        self, content_by_pair: dict[tuple[str, str], bytes]
    ) -> dict[tuple[str, str], UUID]:
        if not content_by_pair:
            return {}
        created_rows = self.create_many(
            [
                {
                    "question_number_id": question_number_id,
                    "url": url,
                    "content": content,
                }
                for (question_number_id, url), content in content_by_pair.items()
            ],
            auto_commit=False,
        )
        return {(row.question_number_id, row.url): row.id for row in created_rows}

    def get_by_question_and_url(
        self, question_number_id: str, url: str
    ) -> QuestionFileDTO | None:
        entity = self.get_one_or_none(
            question_number_id=question_number_id, url=url
        )
        return QuestionFileDTO.from_entity(entity) if entity is not None else None
