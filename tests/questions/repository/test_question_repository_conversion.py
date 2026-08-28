from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from questions.dtos.question_scraped_dto import QuestionScrapedDTO
from questions.entity.questao import Questao
from questions.repository.question_repository import QuestionRepository


def test_scraped_dto_is_converted_to_entity_without_a_mapper():
    """O DTO cai direto na entidade porque seus campos já têm o nome das colunas."""
    session = Session(create_engine("sqlite://"))
    repo = QuestionRepository(session=session)

    entity = repo.to_model(
        QuestionScrapedDTO(
            question_id="Q1",
            subject="Física",
            topics=["Óptica"],
            alternatives={"A": {"text": "x", "images": []}},
        ),
        "upsert",
    )

    assert isinstance(entity, Questao)
    assert entity.question_id == "Q1"
    assert entity.subject == "Física"
    assert entity.topics == ["Óptica"]
    assert entity.alternatives == {"A": {"text": "x", "images": []}}
