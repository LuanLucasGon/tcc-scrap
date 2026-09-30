from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from subject.dtos.subject_dto import SubjectDTO


class SubjectRepositoryInterface(ABC):
    """Porta de persistência para matérias."""

    @abstractmethod
    def get_or_create_many(self, raw_names: list[str]) -> dict[str, UUID]:
        """Normaliza cada nome, cria as matérias que faltam.

        Devolve ``{nome_raw: id}``.
        """

    @abstractmethod
    def get_by_name(self, name: str) -> SubjectDTO | None:
        """Busca a matéria pelo nome (o argumento é normalizado antes do lookup)."""

    @abstractmethod
    def list_active(self) -> list[SubjectDTO]:
        """Lista as matérias com ``deleted = false`` e ``active = true``."""
