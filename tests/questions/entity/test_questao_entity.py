def test_questao_entity_is_exposed_from_questions_package():
    from questions.entity.questao import Questao

    assert Questao.__tablename__ == "questao"
    columns = set(Questao.__table__.columns.keys())
    assert {"question_id", "alternatives", "excluido", "created_at", "updated_at"} <= columns


def test_questao_entity_shares_metadata_with_infra_base():
    from infra.database import Base
    from questions.entity.questao import Questao

    assert Questao.metadata is Base.metadata
