import uuid
from datetime import datetime, timezone

from questionfile.dtos.question_file_dto import QuestionFileDTO
from questionfile.entity.question_file import QuestionFile


def test_from_entity_maps_fields_without_the_binary_content():
    entity_id = uuid.uuid4()
    now = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)
    entity = QuestionFile(
        id=entity_id,
        question_number_id="Q3761251",
        url="https://example.com/imagem.png",
        content=b"\x89PNG...",
        active=True,
        deleted=False,
        created_at=now,
        updated_at=now,
    )

    dto = QuestionFileDTO.from_entity(entity)

    assert dto.id == str(entity_id)
    assert dto.question_number_id == "Q3761251"
    assert dto.url == "https://example.com/imagem.png"
    assert dto.active is True
    assert dto.deleted is False
    assert dto.created_at == now
    assert dto.updated_at == now
    assert not hasattr(dto, "content")
