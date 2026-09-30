import uuid

import pytest

from subject.entity.subject import Subject
from subject.repository.subject_repository import SubjectRepository


def test_get_or_create_many_creates_missing_subjects(db_session):
    repo = SubjectRepository(session=db_session)

    result = repo.get_or_create_many(["Matemática", "História"])

    assert set(result) == {"Matemática", "História"}
    names = {s.name for s in db_session.query(Subject).all()}
    assert {"MATEMATICA", "HISTORIA"} <= names


def test_get_or_create_many_reuses_existing_row(db_session):
    repo = SubjectRepository(session=db_session)
    first = repo.get_or_create_many(["Matemática"])

    second = repo.get_or_create_many(["Matemática"])

    assert first["Matemática"] == second["Matemática"]
    count = db_session.query(Subject).filter_by(name="MATEMATICA").count()
    assert count == 1


def test_get_or_create_many_dedupes_names_that_normalize_equal(db_session):
    repo = SubjectRepository(session=db_session)

    result = repo.get_or_create_many(["Matemática", "  matematica ", "MATEMÁTICA"])

    assert len({result[name] for name in result}) == 1
    assert db_session.query(Subject).filter_by(name="MATEMATICA").count() == 1


def test_get_or_create_many_raises_when_name_normalizes_to_empty(db_session):
    repo = SubjectRepository(session=db_session)

    with pytest.raises(ValueError):
        repo.get_or_create_many(["Matemática", "!!!"])


def test_get_by_name_normalizes_its_argument(db_session):
    repo = SubjectRepository(session=db_session)
    repo.get_or_create_many(["Matemática"])

    dto = repo.get_by_name("  matemática ")

    assert dto is not None
    assert dto.name == "MATEMATICA"


def test_get_by_name_returns_none_when_missing(db_session):
    repo = SubjectRepository(session=db_session)

    assert repo.get_by_name(f"missing-{uuid.uuid4()}") is None


def test_list_active_excludes_deleted_and_inactive(db_session):
    repo = SubjectRepository(session=db_session)
    repo.get_or_create_many(["Ativa", "Excluida", "Inativa"])
    db_session.query(Subject).filter_by(name="EXCLUIDA").update({"deleted": True})
    db_session.query(Subject).filter_by(name="INATIVA").update({"active": False})

    names = {dto.name for dto in repo.list_active()}

    assert "ATIVA" in names
    assert "EXCLUIDA" not in names
    assert "INATIVA" not in names
