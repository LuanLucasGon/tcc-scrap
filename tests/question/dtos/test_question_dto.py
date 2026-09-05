import uuid
from datetime import datetime, timezone

from question.dtos.question_dto import QuestionDTO
from question.entity.question import Question
from subject.entity.subject import Subject


def test_from_entity_exposes_subject_id_and_name():
    entity_id = uuid.uuid4()
    subject_id = uuid.uuid4()
    now = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
    entity = Question(
        id=entity_id,
        question_id="Q42",
        subject_id=subject_id,
        subject=Subject(id=subject_id, name="HISTORIA"),
        topics=["Brasil Colônia"],
        alternatives={"A": {"text": "x", "images": []}},
        deleted=False,
        created_at=now,
        updated_at=now,
    )

    dto = QuestionDTO.from_entity(entity)

    assert dto.id == str(entity_id)
    assert dto.question_id == "Q42"
    assert dto.subject_id == str(subject_id)
    assert dto.subject_name == "HISTORIA"
    assert dto.topics == ["Brasil Colônia"]
    assert dto.alternatives == {"A": {"text": "x", "images": []}}
    assert dto.deleted is False
    assert dto.created_at == now


def test_from_entity_tolerates_missing_subject_relationship_and_null_collections():
    entity = Question(
        id=uuid.uuid4(),
        question_id="Q1",
        subject_id=uuid.uuid4(),
        topics=None,
        alternatives=None,
    )

    dto = QuestionDTO.from_entity(entity)

    assert dto.subject_name is None
    assert dto.topics == []
    assert dto.alternatives == {}
