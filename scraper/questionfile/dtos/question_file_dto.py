from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from questionfile.entity.question_file import QuestionFile


@dataclass
class QuestionFileDTO:
    """Um arquivo de questão como ele é entregue para quem consome o repositório.

    Não carrega o binário (``content``) — evita puxar blobs grandes à toa em
    consultas que só precisam do ``id``/``url``. Buscar o conteúdo em si é
    responsabilidade de um método dedicado, a ser adicionado quando houver
    um consumidor real (ex.: servir a imagem de volta).
    """

    id: str
    question_number_id: str
    url: str
    active: bool
    deleted: bool
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_entity(cls, entity: QuestionFile) -> QuestionFileDTO:
        return cls(
            id=str(entity.id),
            question_number_id=entity.question_number_id,
            url=entity.url,
            active=bool(entity.active),
            deleted=bool(entity.deleted),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
