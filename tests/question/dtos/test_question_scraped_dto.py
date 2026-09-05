from question.dtos.question_scraped_dto import QuestionScrapedDTO


def test_from_scrape_builds_dto_from_snake_case_payload():
    payload = {
        "question_id": "Q123",
        "subject": "Matemática",
        "topics": ["Álgebra", "Funções"],
        "year": "2022",
        "exam_board": "INEP",
        "organization": "ENEM",
        "exam_title": "ENEM 2022",
        "exam_url": "https://example.com/prova",
        "associated_text": "Texto base",
        "enunciation": "Qual o valor de x?",
        "alternatives": {"A": {"text": "1", "images": []}},
        "correct_answer": "A",
    }

    dto = QuestionScrapedDTO.from_scrape(payload)

    assert dto.question_id == "Q123"
    assert dto.subject == "Matemática"
    assert dto.topics == ["Álgebra", "Funções"]
    assert dto.year == "2022"
    assert dto.exam_board == "INEP"
    assert dto.organization == "ENEM"
    assert dto.exam_title == "ENEM 2022"
    assert dto.exam_url == "https://example.com/prova"
    assert dto.associated_text == "Texto base"
    assert dto.enunciation == "Qual o valor de x?"
    assert dto.alternatives == {"A": {"text": "1", "images": []}}
    assert dto.correct_answer == "A"


def test_from_scrape_defaults_missing_optional_fields():
    dto = QuestionScrapedDTO.from_scrape({"question_id": "Q1"})

    assert dto.question_id == "Q1"
    assert dto.subject is None
    assert dto.topics == []
    assert dto.alternatives == {}
    assert dto.exam_url is None
    assert dto.correct_answer is None
