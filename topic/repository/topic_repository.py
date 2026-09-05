from __future__ import annotations

from uuid import UUID

from advanced_alchemy.repository import SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemySyncRepositoryService

from shared.normalization import normalize_many, normalize_name
from topic.dtos.topic_dto import TopicDTO
from topic.entity.topic import Topic
from topic.repository.topic_repository_interface import TopicRepositoryInterface


class _TopicRepository(SQLAlchemySyncRepository[Topic]):
    model_type = Topic


class TopicRepository(
    SQLAlchemySyncRepositoryService[Topic, _TopicRepository],
    TopicRepositoryInterface,
):
    """Persistência de tópicos sobre o service layer do Advanced Alchemy.

    Recebe a ``Session`` de quem chama; a transação é do chamador. Cada tópico
    pertence a um ``subject_id`` — o mesmo nome normalizado pode existir em
    matérias diferentes sem conflito (``UNIQUE(subject_id, name)``).
    """

    repository_type = _TopicRepository

    def get_or_create_many(
        self, subject_id: UUID, raw_names: list[str]
    ) -> dict[str, UUID]:
        normalized_name_by_raw_name = normalize_many(raw_names, entity_label="tópico")
        normalized_names = set(normalized_name_by_raw_name.values())

        id_by_normalized_name = {
            topic.name: topic.id
            for topic in self.get_many(
                Topic.subject_id == subject_id, Topic.name.in_(normalized_names)
            )
        }

        missing_names = sorted(normalized_names - id_by_normalized_name.keys())
        if missing_names:
            created_topics = self.create_many(
                [{"name": name, "subject_id": subject_id} for name in missing_names],
                auto_commit=False,
            )
            id_by_normalized_name.update(
                {topic.name: topic.id for topic in created_topics}
            )

        return {
            raw_name: id_by_normalized_name[normalized_name]
            for raw_name, normalized_name in normalized_name_by_raw_name.items()
        }

    def get_by_name(self, subject_id: UUID, name: str) -> TopicDTO | None:
        entity = self.get_one_or_none(
            subject_id=subject_id, name=normalize_name(name)
        )
        return TopicDTO.from_entity(entity) if entity is not None else None

    def list_active(self, subject_id: UUID) -> list[TopicDTO]:
        return [
            TopicDTO.from_entity(topic)
            for topic in self.get_many(
                Topic.subject_id == subject_id,
                Topic.deleted.is_(False),
                Topic.active.is_(True),
            )
        ]
