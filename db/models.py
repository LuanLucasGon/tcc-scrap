import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Questao(Base):
    __tablename__ = "questao"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    question_id: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    subject: Mapped[str | None] = mapped_column(String)
    topics: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    year: Mapped[str | None] = mapped_column(String)
    exam_board: Mapped[str | None] = mapped_column(String)
    organization: Mapped[str | None] = mapped_column(String)
    exam_title: Mapped[str | None] = mapped_column(String)
    exam_url: Mapped[str | None] = mapped_column(String)

    associated_text: Mapped[str | None] = mapped_column(Text)
    enunciation: Mapped[str | None] = mapped_column(Text)
    alternatives: Mapped[dict | None] = mapped_column(JSONB)

    excluido: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Questao question_id={self.question_id!r} excluido={self.excluido}>"
