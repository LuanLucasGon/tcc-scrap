import uuid

from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.entity.question import Question
from question.repository.question_repository import QuestionRepository
from question.repository.upsert_result import UpsertResult
from subject.repository.subject_repository import SubjectRepository


def _dto(question_id: str, **overrides) -> QuestionScrapedDTO:
    base = dict(question_id=question_id, subject="Matemática", topics=["Álgebra"])
    base.update(overrides)
    return QuestionScrapedDTO(**base)


def _subject_id_by_name(session, *names) -> dict[str, uuid.UUID]:
    return SubjectRepository(session=session).get_or_create_many(list(names))


def test_upsert_many_reports_all_inserted_on_first_run(db_session):
    repo = QuestionRepository(session=db_session)
    subject_ids = _subject_id_by_name(db_session, "Matemática")

    result = repo.upsert_many([_dto("Q1"), _dto("Q2")], subject_ids)

    assert result == UpsertResult(inserted=2, updated=0)
    assert repo.get_by_question_id("Q1").subject_name == "MATEMATICA"


def test_upsert_many_links_the_given_subject_id(db_session):
    repo = QuestionRepository(session=db_session)
    subject_ids = _subject_id_by_name(db_session, "História Geral")

    repo.upsert_many([_dto("Q1", subject="História Geral")], subject_ids)

    question = db_session.query(Question).filter_by(question_id="Q1").one()
    assert question.subject_id == subject_ids["História Geral"]


def test_upsert_many_updates_existing_and_inserts_new(db_session):
    repo = QuestionRepository(session=db_session)
    subject_ids = _subject_id_by_name(db_session, "Matemática")
    repo.upsert_many([_dto("Q1", enunciation="antigo")], subject_ids)

    result = repo.upsert_many([_dto("Q1", enunciation="novo"), _dto("Q2")], subject_ids)

    assert result == UpsertResult(inserted=1, updated=1)
    assert repo.get_by_question_id("Q1").enunciation == "novo"


def test_reupsert_does_not_resurrect_a_soft_deleted_question(db_session):
    repo = QuestionRepository(session=db_session)
    subject_ids = _subject_id_by_name(db_session, "Matemática")
    repo.upsert_many([_dto("Q1")], subject_ids)
    db_session.query(Question).filter_by(question_id="Q1").update({"deleted": True})

    repo.upsert_many([_dto("Q1", enunciation="reprocessado")], subject_ids)

    row = db_session.query(Question).filter_by(question_id="Q1").one()
    assert row.deleted is True
    assert row.enunciation == "reprocessado"


def test_upsert_many_returns_no_op_result_for_empty_list(db_session):
    repo = QuestionRepository(session=db_session)

    result = repo.upsert_many([], {})

    assert result == UpsertResult(inserted=0, updated=0)


def test_list_active_excludes_soft_deleted(db_session):
    repo = QuestionRepository(session=db_session)
    subject_ids = _subject_id_by_name(db_session, "Matemática")
    repo.upsert_many([_dto("Q1"), _dto("Q2")], subject_ids)
    db_session.query(Question).filter_by(question_id="Q2").update({"deleted": True})

    active_ids = {dto.question_id for dto in repo.list_active()}

    assert "Q1" in active_ids
    assert "Q2" not in active_ids


def test_get_by_question_id_returns_none_when_missing(db_session):
    repo = QuestionRepository(session=db_session)

    assert repo.get_by_question_id(f"missing-{uuid.uuid4()}") is None
