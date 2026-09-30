import uuid

from main import find_image_urls, replace_image_markers
from question.dtos.question_scraped_dto import QuestionScrapedDTO


def _dto(**overrides) -> QuestionScrapedDTO:
    base = dict(question_id="Q1", subject="Matemática")
    base.update(overrides)
    return QuestionScrapedDTO(**base)


def test_find_image_urls_collects_from_enunciation_associated_text_and_alternatives():
    dto = _dto(
        enunciation="Texto\n[IMAGE] https://example.com/a.png",
        associated_text="Base\n[IMAGE] https://example.com/b.png",
        alternatives={
            "A": {"text": "1", "images": ["https://example.com/c.png"]},
            "B": {"text": "2", "images": []},
        },
    )

    urls = find_image_urls(dto)

    assert urls == {
        "https://example.com/a.png",
        "https://example.com/b.png",
        "https://example.com/c.png",
    }


def test_find_image_urls_dedupes_the_same_url_in_multiple_places():
    dto = _dto(
        enunciation="[IMAGE] https://example.com/a.png",
        alternatives={"A": {"text": "1", "images": ["https://example.com/a.png"]}},
    )

    assert find_image_urls(dto) == {"https://example.com/a.png"}


def test_find_image_urls_returns_empty_set_when_no_images():
    dto = _dto(enunciation="Sem imagem aqui.")

    assert find_image_urls(dto) == set()


def test_replace_image_markers_rewrites_resolved_urls_in_text_fields():
    file_id = uuid.uuid4()
    dto = _dto(
        enunciation="Texto\n[IMAGE] https://example.com/a.png\nFim",
        associated_text="Base\n[IMAGE] https://example.com/a.png",
    )

    result = replace_image_markers(dto, {"https://example.com/a.png": file_id})

    assert result.enunciation == f"Texto\n[IMAGE:{file_id}]\nFim"
    assert result.associated_text == f"Base\n[IMAGE:{file_id}]"


def test_replace_image_markers_rewrites_resolved_urls_in_alternatives():
    file_id = uuid.uuid4()
    dto = _dto(
        alternatives={
            "A": {"text": "1", "images": ["https://example.com/a.png"]},
            "B": {"text": "2", "images": []},
        }
    )

    result = replace_image_markers(dto, {"https://example.com/a.png": file_id})

    assert result.alternatives["A"]["images"] == [f"[IMAGE:{file_id}]"]
    assert result.alternatives["A"]["text"] == "1"
    assert result.alternatives["B"]["images"] == []


def test_replace_image_markers_keeps_unresolved_urls_untouched():
    dto = _dto(
        enunciation="[IMAGE] https://example.com/falhou.png",
        alternatives={"A": {"text": "1", "images": ["https://example.com/falhou.png"]}},
    )

    result = replace_image_markers(dto, {})

    assert result.enunciation == "[IMAGE] https://example.com/falhou.png"
    assert result.alternatives["A"]["images"] == ["https://example.com/falhou.png"]


def test_replace_image_markers_does_not_mutate_the_original_dto():
    dto = _dto(
        enunciation="[IMAGE] https://example.com/a.png",
        alternatives={"A": {"text": "1", "images": ["https://example.com/a.png"]}},
    )
    file_id = uuid.uuid4()

    replace_image_markers(dto, {"https://example.com/a.png": file_id})

    assert dto.enunciation == "[IMAGE] https://example.com/a.png"
    assert dto.alternatives["A"]["images"] == ["https://example.com/a.png"]


def test_replace_image_markers_tolerates_none_text_fields():
    dto = _dto(enunciation=None, associated_text=None)

    result = replace_image_markers(dto, {})

    assert result.enunciation is None
    assert result.associated_text is None
