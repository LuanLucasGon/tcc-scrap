import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    LargeBinary,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infra.database import Base


class QuestionFile(Base):
    """Modelo SQLAlchemy da tabela ``questionfile``.

    Guarda o binário de cada imagem referenciada por uma questão do scraper.
    A identidade é o par ``(question_number_id, url)``: a mesma URL citada por
    duas questões diferentes vira duas linhas (o download, porém, acontece uma
    vez só — ver ``main.persist_images``).
    """

    __tablename__ = "questionfile"
    __table_args__ = (
        UniqueConstraint(
            "question_number_id", "url", name="uq_questionfile_question_number_id_url"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    question_number_id: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String, nullable=False, index=True)
    content: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)

    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
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
        return (
            f"<QuestionFile question_number_id={self.question_number_id!r} "
            f"url={self.url!r} bytes={len(self.content or b'')}>"
        )
