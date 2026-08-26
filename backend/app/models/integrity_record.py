from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class IntegrityRecord(Base):
    __tablename__ = "integrity_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    metadata_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    ocr_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    spatial_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    verification_hash: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
