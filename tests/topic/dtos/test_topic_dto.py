import uuid
from datetime import datetime, timezone

from topic.dtos.topic_dto import TopicDTO
from topic.entity.topic import Topic


def test_from_entity_maps_all_fields():
    entity_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    now = datetime(2026, 9, 4, 12, 0, tzinfo=timezone.utc)
    entity = Topic(
        id=entity_id,
        subject_id=subject_id,
        name="HISTORIA_GERAL",
        active=True,
        deleted=False,
        created_at=now,
        updated_at=now,
    )

    dto = TopicDTO.from_entity(entity)

    assert dto.id == str(entity_id)
    assert dto.name == "HISTORIA_GERAL"
    assert dto.subject_id == str(subject_id)
    assert dto.active is True
    assert dto.deleted is False
    assert dto.created_at == now
    assert dto.updated_at == now
