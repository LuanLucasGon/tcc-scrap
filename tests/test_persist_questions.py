import uuid

import pytest

from main import persist_questions
from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.entity.question import Question
from question.repository.upsert_result import UpsertResult
from shared.normalization import normalize_name
from subject.entity.subject import Subject
from topic.entity.topic import Topic


def _dto(question_id: str, **overrides) -> QuestionScrapedDTO:
    base = dict(question_id=question_id, subject="Matemática", topics=["Álgebra"])
    base.update(overrides)
    return QuestionScrapedDTO(**base)


def test_persist_questions_creates_subject_and_links_question(db_session):
    result = persist_questions(db_session, [_dto("Q1", subject="História Geral")])

    assert result == UpsertResult(inserted=1, updated=0)
    subject = db_session.query(Subject).filter_by(name="HISTORIA_GERAL").one()
    question = db_session.query(Question).filter_by(question_id="Q1").one()
    assert question.subject_id == subject.id


def test_persist_questions_reuses_existing_subject_across_calls(db_session):
    persist_questions(db_session, [_dto("Q1", subject="Matemática")])

    persist_questions(db_session, [_dto("Q2", subject="  matematica ")])

    assert db_session.query(Subject).filter_by(name="MATEMATICA").count() == 1


def test_persist_questions_raises_when_question_has_no_subject(db_session):
    with pytest.raises(ValueError):
        persist_questions(db_session, [_dto("Q1", subject="")])


def test_persist_questions_creates_topics_linked_to_the_question_subject(db_session):
    persist_questions(
        db_session, [_dto("Q1", subject="Matemática", topics=["Álgebra", "Geometria"])]
    )

    subject = db_session.query(Subject).filter_by(name="MATEMATICA").one()
    topic_names = {
        topic.name
        for topic in db_session.query(Topic).filter_by(subject_id=subject.id)
    }
    assert {"ALGEBRA", "GEOMETRIA"} <= topic_names


def test_persist_questions_reuses_existing_topics_across_calls(db_session):
    dto1 = _dto("Q1", subject="Matemática", topics=["Álgebra"])
    dto2 = _dto("Q2", subject="Matemática", topics=["Álgebra"])

    persist_questions(db_session, [dto1])
    persist_questions(db_session, [dto2])

    subject = db_session.query(Subject).filter_by(name="MATEMATICA").one()
    count = (
        db_session.query(Topic)
        .filter_by(subject_id=subject.id, name="ALGEBRA")
        .count()
    )
    assert count == 1


def test_persist_questions_same_topic_name_stays_independent_per_subject(db_session):
    # Nomes exclusivos deste teste — ver comentário em
    # test_persist_questions_skips_topic_creation_when_dto_has_no_topics.
    subject_a = f"Matéria A {uuid.uuid4()}"
    subject_b = f"Matéria B {uuid.uuid4()}"
    persist_questions(db_session, [_dto("Q1", subject=subject_a, topics=["Geral"])])
    persist_questions(db_session, [_dto("Q2", subject=subject_b, topics=["Geral"])])

    subject_ids = [
        subject.id
        for subject in db_session.query(Subject).filter(
            Subject.name.in_([normalize_name(subject_a), normalize_name(subject_b)])
        )
    ]
    count = (
        db_session.query(Topic)
        .filter(Topic.subject_id.in_(subject_ids), Topic.name == "GERAL")
        .count()
    )
    assert count == 2


def test_persist_questions_skips_topic_creation_when_dto_has_no_topics(db_session):
    # Nome exclusivo deste teste: "Matemática"/"História" etc. já existem com
    # tópicos reais no banco de dev compartilhado (o scraper roda contra o
    # mesmo Postgres), então "zero tópicos" só é uma asserção segura para uma
    # matéria que nada além deste teste poderia ter criado.
    subject_name = f"Matéria sem tópicos {uuid.uuid4()}"
    persist_questions(db_session, [_dto("Q1", subject=subject_name, topics=[])])

    subject = (
        db_session.query(Subject)
        .filter_by(name=normalize_name(subject_name))
        .one()
    )
    assert db_session.query(Topic).filter_by(subject_id=subject.id).count() == 0


def test_persist_questions_returns_no_op_result_for_empty_list(db_session):
    result = persist_questions(db_session, [])

    assert result == UpsertResult(inserted=0, updated=0)
