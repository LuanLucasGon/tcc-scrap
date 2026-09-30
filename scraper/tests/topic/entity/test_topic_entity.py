def test_topic_entity_table_and_columns():
    from topic.entity.topic import Topic

    assert Topic.__tablename__ == "topic"
    columns = Topic.__table__.columns
    assert set(columns.keys()) == {
        "id",
        "subject_id",
        "name",
        "active",
        "deleted",
        "created_at",
        "updated_at",
    }
    assert columns["name"].nullable is False
    assert columns["subject_id"].nullable is False
    assert columns["active"].nullable is False
    assert columns["deleted"].nullable is False


def test_topic_has_not_null_fk_to_subject():
    from topic.entity.topic import Topic

    fk = next(iter(Topic.__table__.c.subject_id.foreign_keys))
    assert fk.column.table.name == "subject"
    assert Topic.__table__.c.subject_id.nullable is False


def test_topic_name_is_unique_per_subject_not_globally():
    from topic.entity.topic import Topic

    unique_constraints = [
        constraint
        for constraint in Topic.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]
    assert len(unique_constraints) == 1
    columns = {column.name for column in unique_constraints[0].columns}
    assert columns == {"subject_id", "name"}
    assert Topic.__table__.columns["name"].unique is not True


def test_topic_shares_metadata_with_infra_base():
    from infra.database import Base
    from topic.entity.topic import Topic

    assert Topic.metadata is Base.metadata
