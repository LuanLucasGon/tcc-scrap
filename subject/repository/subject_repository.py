from __future__ import annotations

from uuid import UUID

from advanced_alchemy.repository import SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemySyncRepositoryService

from subject.dtos.subject_dto import SubjectDTO
from subject.entity.subject import Subject
from subject.normalization import normalize_subject_name
from subject.repository.subject_repository_interface import SubjectRepositoryInterface


class _SubjectRepository(SQLAlchemySyncRepository[Subject]):
    model_type = Subject


class SubjectRepository(
    SQLAlchemySyncRepositoryService[Subject, _SubjectRepository],
    SubjectRepositoryInterface,
):
    """Persistência de matérias sobre o service layer do Advanced Alchemy.

    Recebe a ``Session`` de quem chama; a transação é do chamador.
    """

    repository_type = _SubjectRepository

    def get_or_create_many(self, raw_names: list[str]) -> dict[str, UUID]:
        normalized_name_by_raw_name = self._normalize_and_validate(raw_names)
        normalized_names = set(normalized_name_by_raw_name.values())

        id_by_normalized_name = {
            subject.name: subject.id
            for subject in self.get_many(Subject.name.in_(normalized_names))
        }

        missing_names = sorted(normalized_names - id_by_normalized_name.keys())
        if missing_names:
            created_subjects = self.create_many(
                [{"name": name} for name in missing_names], auto_commit=False
            )
            id_by_normalized_name.update(
                {subject.name: subject.id for subject in created_subjects}
            )

        return {
            raw_name: id_by_normalized_name[normalized_name]
            for raw_name, normalized_name in normalized_name_by_raw_name.items()
        }

    @staticmethod
    def _normalize_and_validate(raw_names: list[str]) -> dict[str, str]:
        """Mapeia cada nome cru distinto para sua forma normalizada.

        Levanta ``ValueError`` se algum nome normalizar para string vazia.
        """
        normalized_name_by_raw_name = {
            raw_name: normalize_subject_name(raw_name)
            for raw_name in dict.fromkeys(raw_names)
        }
        for raw_name, normalized_name in normalized_name_by_raw_name.items():
            if not normalized_name:
                raise ValueError(
                    f"nome de matéria inválido (normaliza para vazio): {raw_name!r}"
                )
        return normalized_name_by_raw_name

    def get_by_name(self, name: str) -> SubjectDTO | None:
        entity = self.get_one_or_none(name=normalize_subject_name(name))
        return SubjectDTO.from_entity(entity) if entity is not None else None

    def list_active(self) -> list[SubjectDTO]:
        return [
            SubjectDTO.from_entity(subject)
            for subject in self.get_many(
                Subject.deleted.is_(False), Subject.active.is_(True)
            )
        ]
