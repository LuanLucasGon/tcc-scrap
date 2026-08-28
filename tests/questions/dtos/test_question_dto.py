import uuid
from datetime import datetime, timezone

from questions.dtos.question_dto import QuestionDTO
from questions.entity.questao import Questao


def test_from_entity_copies_fields_and_stringifies_id():
    entity_id = uuid.uuid4()
    now = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
    entity = Questao(
        id=entity_id,
        question_id="Q42",
        subject="História",
        topics=["Brasil Colônia"],
        year="2021",
        exam_board="INEP",
        organization="ENEM",
        exam_title="ENEM 2021",
        exam_url="https://example.com/p",
        associated_text="base",
        enunciation="pergunta",
        alternatives={"A": {"text": "x", "images": []}},
        excluido=False,
        created_at=now,
        updated_at=now,
    )

    dto = QuestionDTO.from_entity(entity)

    assert dto.id == str(entity_id)
    assert dto.question_id == "Q42"
    assert dto.subject == "História"
    assert dto.topics == ["Brasil Colônia"]
    assert dto.alternatives == {"A": {"text": "x", "images": []}}
    assert dto.excluido is False
    assert dto.created_at == now
    assert dto.updated_at == now


def test_from_entity_tolerates_null_collections():
    entity = Questao(id=uuid.uuid4(), question_id="Q1", topics=None, alternatives=None)

    dto = QuestionDTO.from_entity(entity)

    assert dto.topics == []
    assert dto.alternatives == {}
