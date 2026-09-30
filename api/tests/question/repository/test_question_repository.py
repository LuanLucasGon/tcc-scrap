import pytest


def test_question_repository_conforms_to_interface():
    from question.repository.question_repository import QuestionRepository
    from question.repository.question_repository_interface import (
        QuestionRepositoryInterface,
    )

    assert issubclass(QuestionRepository, QuestionRepositoryInterface)


def test_question_repository_get_by_question_id_not_implemented_yet():
    from question.repository.question_repository import QuestionRepository

    repository = QuestionRepository(session=None)

    with pytest.raises(NotImplementedError):
        repository.get_by_question_id("Q123")
