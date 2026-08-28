import uuid

from questions.dtos.question_scraped_dto import QuestionScrapedDTO
from questions.entity.questao import Questao
from questions.repository.question_repository import QuestionRepository
from questions.repository.upsert_result import UpsertResult


def _dto(question_id: str, **overrides) -> QuestionScrapedDTO:
    base = dict(question_id=question_id, subject="Matemática", topics=["Álgebra"])
    base.update(overrides)
    return QuestionScrapedDTO(**base)


def test_upsert_many_reports_all_inserted_on_first_run(db_session):
    repo = QuestionRepository(session=db_session)

    result = repo.upsert_many([_dto("Q1"), _dto("Q2")])

    assert result == UpsertResult(inserted=2, updated=0)
    assert repo.get_by_question_id("Q1").subject == "Matemática"


def test_upsert_many_updates_existing_and_inserts_new(db_session):
    repo = QuestionRepository(session=db_session)
    repo.upsert_many([_dto("Q1", subject="antigo")])

    result = repo.upsert_many([_dto("Q1", subject="novo"), _dto("Q2")])

    assert result == UpsertResult(inserted=1, updated=1)
    assert repo.get_by_question_id("Q1").subject == "novo"


def test_list_active_excludes_soft_deleted(db_session):
    repo = QuestionRepository(session=db_session)
    repo.upsert_many([_dto("Q1"), _dto("Q2")])
    db_session.query(Questao).filter_by(question_id="Q2").update({"excluido": True})

    active_ids = {dto.question_id for dto in repo.list_active()}

    assert "Q1" in active_ids
    assert "Q2" not in active_ids


def test_get_by_question_id_returns_none_when_missing(db_session):
    repo = QuestionRepository(session=db_session)

    assert repo.get_by_question_id(f"missing-{uuid.uuid4()}") is None
