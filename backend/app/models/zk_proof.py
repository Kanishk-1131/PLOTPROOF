from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ZKProofRecord(Base):
    """
    Stores Zero-Knowledge Proof metadata without storing private inputs, secrets, or witnesses (Section 19).
    """
    __tablename__ = "zk_proof_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    proof_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    commitment: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    public_signals: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    proof_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    circuit_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="land-verification-v1",
    )

    verification_key_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="vk-v1",
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
