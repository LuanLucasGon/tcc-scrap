import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import ARRAY, JSONB


def test_question_entity_maps_to_question_table():
    from question.entity.question import Question

    assert Question.__tablename__ == "question"
    columns = set(Question.__table__.columns.keys())
    expected = {
        "id",
        "question_id",
        "subject_id",
        "topics",
        "year",
        "exam_board",
        "organization",
        "exam_title",
        "exam_url",
        "associated_text",
        "enunciation",
        "alternatives",
        "correct_answer",
        "deleted",
        "created_at",
        "updated_at",
    }
    assert expected <= columns


def test_question_entity_column_types_match_existing_schema():
    from question.entity.question import Question

    assert isinstance(Question.__table__.c.topics.type, ARRAY)
    assert isinstance(Question.__table__.c.alternatives.type, JSONB)
    assert Question.__table__.c.id.primary_key is True
    assert Question.__table__.c.question_id.nullable is False


def test_question_entity_can_be_instantiated():
    from question.entity.question import Question

    question = Question(
        id=uuid.uuid4(),
        question_id="Q123",
        subject_id=uuid.uuid4(),
        deleted=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert question.question_id == "Q123"
    assert question.deleted is False
