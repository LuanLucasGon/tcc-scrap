def test_question_entity_is_exposed_from_question_package():
    from question.entity.question import Question

    assert Question.__tablename__ == "question"
    columns = set(Question.__table__.columns.keys())
    expected = {
        "question_id",
        "subject_id",
        "alternatives",
        "correct_answer",
        "deleted",
        "created_at",
        "updated_at",
    }
    assert expected <= columns
    assert "subject" not in columns  # relationship, not a column


def test_question_has_not_null_fk_to_subject():
    from question.entity.question import Question

    fk = next(iter(Question.__table__.c.subject_id.foreign_keys))
    assert fk.column.table.name == "subject"
    assert Question.__table__.c.subject_id.nullable is False


def test_question_entity_shares_metadata_with_infra_base():
    from infra.database import Base
    from question.entity.question import Question

    assert Question.metadata is Base.metadata
