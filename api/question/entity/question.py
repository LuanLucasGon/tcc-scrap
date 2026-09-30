import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    """Mapeamento SQLModel da tabela ``question`` já criada pelo scraper.

    A tabela e o schema são geridos pelas migrations do Alembic em
    ``scraper/``; esta classe só mapeia colunas já existentes — nenhuma
    migration nasce a partir dela.
    """

    __tablename__ = "question"

    id: uuid.UUID = Field(
        sa_column=Column(PostgresUUID(as_uuid=True), primary_key=True)
    )
    question_id: str = Field(unique=True, index=True)
    subject_id: uuid.UUID = Field(
        sa_column=Column(PostgresUUID(as_uuid=True), nullable=False, index=True)
    )
    topics: list[str] | None = Field(
        default=None, sa_column=Column(ARRAY(String))
    )
    year: str | None = None
    exam_board: str | None = None
    organization: str | None = None
    exam_title: str | None = None
    exam_url: str | None = None
    associated_text: str | None = None
    enunciation: str | None = None
    alternatives: dict[str, Any] | None = Field(
        default=None, sa_column=Column(JSONB)
    )
    correct_answer: str | None = None
    deleted: bool = False
    created_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
