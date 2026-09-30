import dataclasses


def test_question_dto_has_expected_fields():
    from question.dtos.question_dto import QuestionDTO

    fields = {f.name for f in dataclasses.fields(QuestionDTO)}
    expected = {
        "id",
        "question_id",
        "subject_id",
        "topics",
        "year",
        "exam_board",
        "organization",
        "exam_title",
        "exam_url",
        "associated_text",
        "enunciation",
        "alternatives",
        "correct_answer",
        "deleted",
        "created_at",
        "updated_at",
    }
    assert expected <= fields
