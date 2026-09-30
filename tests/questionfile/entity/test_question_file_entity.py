def test_question_file_entity_table_and_columns():
    from questionfile.entity.question_file import QuestionFile

    assert QuestionFile.__tablename__ == "questionfile"
    columns = QuestionFile.__table__.columns
    assert set(columns.keys()) == {
        "id",
        "question_number_id",
        "url",
        "content",
        "active",
        "deleted",
        "created_at",
        "updated_at",
    }
    assert columns["question_number_id"].nullable is False
    assert columns["url"].nullable is False
    assert columns["content"].nullable is False
    assert columns["active"].nullable is False
    assert columns["deleted"].nullable is False


def test_question_file_is_unique_by_question_number_id_and_url():
    from sqlalchemy import UniqueConstraint

    from questionfile.entity.question_file import QuestionFile

    unique_column_sets = {
        tuple(sorted(column.name for column in constraint.columns))
        for constraint in QuestionFile.__table__.constraints
        if isinstance(constraint, UniqueConstraint)
    }
    assert ("question_number_id", "url") in unique_column_sets


def test_question_file_shares_metadata_with_infra_base():
    from infra.database import Base
    from questionfile.entity.question_file import QuestionFile

    assert QuestionFile.metadata is Base.metadata
