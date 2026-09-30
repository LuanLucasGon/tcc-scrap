import pytest


def test_question_service_get_by_question_id_not_implemented_yet():
    from question.service.question_service import QuestionService

    service = QuestionService(repository=None)

    with pytest.raises(NotImplementedError):
        service.get_by_question_id("Q123")
