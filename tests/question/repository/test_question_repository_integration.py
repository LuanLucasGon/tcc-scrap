import uuid

import pytest

from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.entity.question import Question
from question.repository.question_repository import QuestionRepository
from question.repository.upsert_result import UpsertResult
from subject.entity.subject import Subject


def _dto(question_id: str, **overrides) -> QuestionScrapedDTO:
    base = dict(question_id=question_id, subject="Matemática", topics=["Álgebra"])
    base.update(overrides)
    return QuestionScrapedDTO(**base)


def test_upsert_many_reports_all_inserted_on_first_run(db_session):
    repo = QuestionRepository(session=db_session)

    result = repo.upsert_many([_dto("Q1"), _dto("Q2")])

    assert result == UpsertResult(inserted=2, updated=0)
    assert repo.get_by_question_id("Q1").subject_name == "MATEMATICA"


def test_upsert_many_creates_subject_row_and_links_fk(db_session):
    repo = QuestionRepository(session=db_session)

    repo.upsert_many([_dto("Q1", subject="História Geral")])

    subject = db_session.query(Subject).filter_by(name="HISTORIA_GERAL").one()
    question = db_session.query(Question).filter_by(question_id="Q1").one()
    assert question.subject_id == subject.id


def test_upsert_many_reuses_existing_subject(db_session):
    repo = QuestionRepository(session=db_session)
    repo.upsert_many([_dto("Q1", subject="Matemática")])

    repo.upsert_many([_dto("Q2", subject="  matematica ")])

    assert db_session.query(Subject).filter_by(name="MATEMATICA").count() == 1
    q1 = db_session.query(Question).filter_by(question_id="Q1").one()
    q2 = db_session.query(Question).filter_by(question_id="Q2").one()
    assert q1.subject_id == q2.subject_id


def test_upsert_many_updates_existing_and_inserts_new(db_session):
    repo = QuestionRepository(session=db_session)
    repo.upsert_many([_dto("Q1", enunciation="antigo")])

    result = repo.upsert_many([_dto("Q1", enunciation="novo"), _dto("Q2")])

    assert result == UpsertResult(inserted=1, updated=1)
    assert repo.get_by_question_id("Q1").enunciation == "novo"


def test_reupsert_does_not_resurrect_a_soft_deleted_question(db_session):
    repo = QuestionRepository(session=db_session)
    repo.upsert_many([_dto("Q1")])
    db_session.query(Question).filter_by(question_id="Q1").update({"deleted": True})

    repo.upsert_many([_dto("Q1", enunciation="reprocessado")])

    row = db_session.query(Question).filter_by(question_id="Q1").one()
    assert row.deleted is True
    assert row.enunciation == "reprocessado"


def test_upsert_many_raises_when_question_has_no_subject(db_session):
    repo = QuestionRepository(session=db_session)

    with pytest.raises(ValueError):
        repo.upsert_many([_dto("Q1", subject="")])


def test_list_active_excludes_soft_deleted(db_session):
    repo = QuestionRepository(session=db_session)
    repo.upsert_many([_dto("Q1"), _dto("Q2")])
    db_session.query(Question).filter_by(question_id="Q2").update({"deleted": True})

    active_ids = {dto.question_id for dto in repo.list_active()}

    assert "Q1" in active_ids
    assert "Q2" not in active_ids


def test_get_by_question_id_returns_none_when_missing(db_session):
    repo = QuestionRepository(session=db_session)

    assert repo.get_by_question_id(f"missing-{uuid.uuid4()}") is None
