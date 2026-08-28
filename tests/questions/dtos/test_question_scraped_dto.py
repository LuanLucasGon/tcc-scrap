from questions.dtos.question_scraped_dto import QuestionScrapedDTO


def test_from_scrape_maps_scraper_payload_to_snake_case_fields():
    payload = {
        "questionId": "Q123",
        "subject": "Matemática",
        "topics": ["Álgebra", "Funções"],
        "year": "2022",
        "examBoard": "INEP",
        "organization": "ENEM",
        "examTitle": "ENEM 2022",
        "examUrl": "https://example.com/prova",
        "associatedText": "Texto base",
        "enunciation": "Qual o valor de x?",
        "alternatives": {"A": {"text": "1", "images": []}},
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


def test_from_scrape_defaults_missing_optional_fields():
    dto = QuestionScrapedDTO.from_scrape({"questionId": "Q1"})

    assert dto.question_id == "Q1"
    assert dto.subject is None
    assert dto.topics == []
    assert dto.alternatives == {}
    assert dto.exam_url is None
