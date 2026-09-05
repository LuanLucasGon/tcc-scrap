import uuid
from datetime import datetime, timezone

from subject.dtos.subject_dto import SubjectDTO
from subject.entity.subject import Subject


def test_from_entity_copies_fields_and_stringifies_id():
    subject_id = uuid.uuid4()
    now = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
    entity = Subject(
        id=subject_id,
        name="MATEMATICA",
        active=True,
        deleted=False,
        created_at=now,
        updated_at=now,
    )

    dto = SubjectDTO.from_entity(entity)

    assert dto.id == str(subject_id)
    assert dto.name == "MATEMATICA"
    assert dto.active is True
    assert dto.deleted is False
    assert dto.created_at == now
    assert dto.updated_at == now
