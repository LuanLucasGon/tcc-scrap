import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from infra.database import Base


class Topic(Base):
    """Modelo SQLAlchemy da tabela ``topic`` (subtópico de um ``subject``)."""

    __tablename__ = "topic"
    __table_args__ = (
        UniqueConstraint("subject_id", "name", name="uq_topic_subject_id_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("subject.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String, nullable=False, index=True)

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
            f"<Topic name={self.name!r} subject_id={self.subject_id} "
            f"active={self.active} deleted={self.deleted}>"
        )
