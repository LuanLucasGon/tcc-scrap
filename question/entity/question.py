import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infra.database import Base
from subject.entity.subject import Subject


class Question(Base):
    """Modelo SQLAlchemy da tabela ``question``."""

    __tablename__ = "question"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    question_id: Mapped[str] = mapped_column(
        String, nullable=False, unique=True, index=True
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subject.id"),
        nullable=False,
        index=True,
    )
    subject: Mapped[Subject] = relationship(lazy="joined")

    topics: Mapped[list[str] | None] = mapped_column(ARRAY(String))
    year: Mapped[str | None] = mapped_column(String)
    exam_board: Mapped[str | None] = mapped_column(String)
    organization: Mapped[str | None] = mapped_column(String)
    exam_title: Mapped[str | None] = mapped_column(String)
    exam_url: Mapped[str | None] = mapped_column(String)

    associated_text: Mapped[str | None] = mapped_column(Text)
    enunciation: Mapped[str | None] = mapped_column(Text)
    alternatives: Mapped[dict | None] = mapped_column(JSONB)

    deleted: Mapped[bool] = mapped_column(
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
        return f"<Question question_id={self.question_id!r} deleted={self.deleted}>"
