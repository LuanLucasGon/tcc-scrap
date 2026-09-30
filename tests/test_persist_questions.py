import uuid

import pytest

from main import persist_questions
from question.dtos.question_scraped_dto import QuestionScrapedDTO
from question.entity.question import Question
from question.repository.upsert_result import UpsertResult
from questionfile.entity.question_file import QuestionFile
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


def test_persist_questions_downloads_and_stores_image_replacing_the_marker(db_session):
    url = f"https://example.com/{uuid.uuid4()}.png"
    dto = _dto(
        "Q1",
        enunciation=f"Texto\n[IMAGE] {url}",
        alternatives={"A": {"text": "1", "images": [url]}},
    )

    def fake_download(requested_url: str) -> bytes | None:
        assert requested_url == url
        return b"PNG-BYTES"

    persist_questions(db_session, [dto], download=fake_download)

    file_row = (
        db_session.query(QuestionFile)
        .filter_by(question_number_id="Q1", url=url)
        .one()
    )
    assert file_row.content == b"PNG-BYTES"

    question = db_session.query(Question).filter_by(question_id="Q1").one()
    marker = f"[IMAGE:{file_row.id}]"
    assert question.enunciation == f"Texto\n{marker}"
    assert question.alternatives["A"]["images"] == [marker]


def test_persist_questions_stores_one_row_per_question_but_downloads_once(db_session):
    url = f"https://example.com/{uuid.uuid4()}.png"
    calls = []

    def fake_download(requested_url: str) -> bytes | None:
        calls.append(requested_url)
        return b"PNG-BYTES"

    dto1 = _dto("Q1", enunciation=f"[IMAGE] {url}")
    dto2 = _dto("Q2", enunciation=f"[IMAGE] {url}")

    persist_questions(db_session, [dto1], download=fake_download)
    persist_questions(db_session, [dto2], download=fake_download)

    assert calls == [url]
    rows = db_session.query(QuestionFile).filter_by(url=url).all()
    assert {row.question_number_id for row in rows} == {"Q1", "Q2"}
    assert {row.content for row in rows} == {b"PNG-BYTES"}


def test_persist_questions_keeps_original_marker_when_download_fails(db_session):
    url = f"https://example.com/{uuid.uuid4()}.png"
    dto = _dto("Q1", enunciation=f"[IMAGE] {url}")

    persist_questions(db_session, [dto], download=lambda _url: None)

    assert db_session.query(QuestionFile).filter_by(url=url).count() == 0
    question = db_session.query(Question).filter_by(question_id="Q1").one()
    assert question.enunciation == f"[IMAGE] {url}"
