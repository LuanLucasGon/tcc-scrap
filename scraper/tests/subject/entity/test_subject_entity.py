def test_subject_entity_table_and_columns():
    from subject.entity.subject import Subject

    assert Subject.__tablename__ == "subject"
    columns = Subject.__table__.columns
    assert set(columns.keys()) == {
        "id",
        "name",
        "active",
        "deleted",
        "created_at",
        "updated_at",
    }
    assert columns["name"].unique is True
    assert columns["name"].nullable is False
    assert columns["active"].nullable is False
    assert columns["deleted"].nullable is False


def test_subject_shares_metadata_with_infra_base():
    from infra.database import Base
    from subject.entity.subject import Subject

    assert Subject.metadata is Base.metadata
