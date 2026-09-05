import uuid

import pytest

from subject.repository.subject_repository import SubjectRepository
from topic.entity.topic import Topic
from topic.repository.topic_repository import TopicRepository


def _subject_id(session, name="Matemática"):
    return SubjectRepository(session=session).get_or_create_many([name])[name]


def test_get_or_create_many_creates_missing_topics(db_session):
    subject_id = _subject_id(db_session)
    repo = TopicRepository(session=db_session)

    result = repo.get_or_create_many(subject_id, ["Álgebra", "Geometria"])

    assert set(result) == {"Álgebra", "Geometria"}
    names = {t.name for t in db_session.query(Topic).filter_by(subject_id=subject_id)}
    assert {"ALGEBRA", "GEOMETRIA"} <= names


def test_get_or_create_many_reuses_existing_row(db_session):
    subject_id = _subject_id(db_session)
    repo = TopicRepository(session=db_session)
    first = repo.get_or_create_many(subject_id, ["Álgebra"])

    second = repo.get_or_create_many(subject_id, ["Álgebra"])

    assert first["Álgebra"] == second["Álgebra"]
    count = (
        db_session.query(Topic)
        .filter_by(subject_id=subject_id, name="ALGEBRA")
        .count()
    )
    assert count == 1


def test_same_topic_name_is_independent_across_subjects(db_session):
    math_id = _subject_id(db_session, "Matemática")
    history_id = _subject_id(db_session, "História")
    repo = TopicRepository(session=db_session)

    math_result = repo.get_or_create_many(math_id, ["Geral"])
    history_result = repo.get_or_create_many(history_id, ["Geral"])

    assert math_result["Geral"] != history_result["Geral"]
    count = (
        db_session.query(Topic)
        .filter(Topic.subject_id.in_([math_id, history_id]), Topic.name == "GERAL")
        .count()
    )
    assert count == 2


def test_get_or_create_many_dedupes_names_that_normalize_equal(db_session):
    subject_id = _subject_id(db_session)
    repo = TopicRepository(session=db_session)

    result = repo.get_or_create_many(subject_id, ["Álgebra", "  algebra ", "ÁLGEBRA"])

    assert len({result[name] for name in result}) == 1
    count = (
        db_session.query(Topic)
        .filter_by(subject_id=subject_id, name="ALGEBRA")
        .count()
    )
    assert count == 1


def test_get_or_create_many_raises_when_name_normalizes_to_empty(db_session):
    subject_id = _subject_id(db_session)
    repo = TopicRepository(session=db_session)

    with pytest.raises(ValueError):
        repo.get_or_create_many(subject_id, ["Álgebra", "!!!"])


def test_get_by_name_normalizes_its_argument(db_session):
    subject_id = _subject_id(db_session)
    repo = TopicRepository(session=db_session)
    repo.get_or_create_many(subject_id, ["Álgebra"])

    dto = repo.get_by_name(subject_id, "  algebra ")

    assert dto is not None
    assert dto.name == "ALGEBRA"
    assert dto.subject_id == str(subject_id)


def test_get_by_name_returns_none_when_missing(db_session):
    subject_id = _subject_id(db_session)
    repo = TopicRepository(session=db_session)

    assert repo.get_by_name(subject_id, f"missing-{uuid.uuid4()}") is None


def test_get_by_name_scopes_lookup_to_the_given_subject(db_session):
    math_id = _subject_id(db_session, "Matemática")
    history_id = _subject_id(db_session, "História")
    repo = TopicRepository(session=db_session)
    repo.get_or_create_many(math_id, ["Geral"])

    assert repo.get_by_name(history_id, "Geral") is None


def test_list_active_excludes_deleted_and_inactive_and_other_subjects(db_session):
    subject_id = _subject_id(db_session, "Matemática")
    other_subject_id = _subject_id(db_session, "História")
    repo = TopicRepository(session=db_session)
    repo.get_or_create_many(subject_id, ["Ativa", "Excluida", "Inativa"])
    repo.get_or_create_many(other_subject_id, ["De Outra Materia"])
    db_session.query(Topic).filter_by(name="EXCLUIDA").update({"deleted": True})
    db_session.query(Topic).filter_by(name="INATIVA").update({"active": False})

    names = {dto.name for dto in repo.list_active(subject_id)}

    assert "ATIVA" in names
    assert "EXCLUIDA" not in names
    assert "INATIVA" not in names
    assert "DE_OUTRA_MATERIA" not in names
