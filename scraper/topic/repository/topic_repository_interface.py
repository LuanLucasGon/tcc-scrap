from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from topic.dtos.topic_dto import TopicDTO


class TopicRepositoryInterface(ABC):
    """Porta de persistência para tópicos (subtópicos de uma matéria)."""

    @abstractmethod
    def get_or_create_many(
        self, subject_id: UUID, raw_names: list[str]
    ) -> dict[str, UUID]:
        """Normaliza cada nome, cria os tópicos que faltam para esse ``subject_id``.

        Devolve ``{nome_raw: id}``.
        """

    @abstractmethod
    def get_by_name(self, subject_id: UUID, name: str) -> TopicDTO | None:
        """Busca o tópico pelo nome dentro de um subject (nome é normalizado antes)."""

    @abstractmethod
    def list_active(self, subject_id: UUID) -> list[TopicDTO]:
        """Lista os tópicos do subject com ``deleted = false`` e ``active = true``."""
