import uuid

import pytest

from questionfile.entity.question_file import QuestionFile
from questionfile.repository.question_file_repository import QuestionFileRepository


def test_get_ids_by_pairs_returns_empty_when_nothing_saved(db_session):
    repo = QuestionFileRepository(session=db_session)

    assert repo.get_ids_by_pairs([("Q1", "https://example.com/a.png")]) == {}


def test_create_missing_creates_a_row_per_question_and_url_pair(db_session):
    repo = QuestionFileRepository(session=db_session)
    content_by_pair = {
        ("Q1", "https://example.com/a.png"): b"AAA",
        ("Q2", "https://example.com/b.png"): b"BBB",
    }

    result = repo.create_missing(content_by_pair)

    assert set(result) == set(content_by_pair)
    saved = {
        (row.question_number_id, row.url): row.content
        for row in db_session.query(QuestionFile)
    }
    assert saved == content_by_pair


def test_get_ids_by_pairs_only_returns_pairs_that_already_exist(db_session):
    repo = QuestionFileRepository(session=db_session)
    a_pair = ("Q1", "https://example.com/a.png")
    created = repo.create_missing({a_pair: b"AAA"})

    result = repo.get_ids_by_pairs(
        [a_pair, ("Q1", "https://example.com/missing.png")]
    )

    assert result == {a_pair: created[a_pair]}


def test_the_same_url_is_stored_once_per_question(db_session):
    repo = QuestionFileRepository(session=db_session)
    url = "https://example.com/a.png"

    repo.create_missing({("Q1", url): b"AAA"})
    repo.create_missing({("Q2", url): b"AAA"})

    assert db_session.query(QuestionFile).filter_by(url=url).count() == 2


def test_create_missing_enforces_the_unique_pair_at_the_database_level(db_session):
    # create_missing assume que quem chama já filtrou com get_ids_by_pairs —
    # este teste documenta que, se isso não acontecer, a constraint de
    # unicidade do banco barra a duplicata.
    repo = QuestionFileRepository(session=db_session)
    pair = ("Q1", "https://example.com/a.png")
    repo.create_missing({pair: b"AAA"})

    with pytest.raises(Exception):
        repo.create_missing({pair: b"BBB"})


def test_get_contents_by_urls_returns_stored_binary_regardless_of_question(db_session):
    repo = QuestionFileRepository(session=db_session)
    url = "https://example.com/a.png"
    repo.create_missing({("Q1", url): b"AAA"})

    assert repo.get_contents_by_urls([url]) == {url: b"AAA"}


def test_get_contents_by_urls_ignores_urls_that_were_never_saved(db_session):
    repo = QuestionFileRepository(session=db_session)

    assert repo.get_contents_by_urls([f"https://example.com/{uuid.uuid4()}.png"]) == {}


def test_get_by_question_and_url_returns_the_matching_row(db_session):
    repo = QuestionFileRepository(session=db_session)
    url = "https://example.com/a.png"
    repo.create_missing({("Q1", url): b"AAA"})

    dto = repo.get_by_question_and_url("Q1", url)

    assert dto is not None
    assert dto.question_number_id == "Q1"
    assert dto.url == url


def test_get_by_question_and_url_returns_none_when_missing(db_session):
    repo = QuestionFileRepository(session=db_session)

    missing_url = f"https://example.com/{uuid.uuid4()}.png"
    assert repo.get_by_question_and_url("Q1", missing_url) is None
