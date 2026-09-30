import json

from main import save_to_json
from question.dtos.question_scraped_dto import QuestionScrapedDTO


def test_save_to_json_serializes_scraped_dtos(tmp_path):
    target = tmp_path / "questions.json"
    dtos = [
        QuestionScrapedDTO(question_id="Q1", subject="Matemática", topics=["Álgebra"]),
        QuestionScrapedDTO(question_id="Q2"),
    ]

    save_to_json(dtos, str(target))

    data = json.loads(target.read_text(encoding="utf-8"))
    assert data[0]["question_id"] == "Q1"
    assert data[0]["topics"] == ["Álgebra"]
    assert data[1]["question_id"] == "Q2"
    assert data[1]["alternatives"] == {}
