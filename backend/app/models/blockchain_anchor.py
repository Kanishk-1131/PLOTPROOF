from datetime import datetime
from typing import Optional
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BlockchainAnchor(Base):
    """
    Persists Polygon / L2 blockchain anchoring transactions for verified land documents (Section 15).
    """
    __tablename__ = "blockchain_anchors"

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

    verification_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    transaction_hash: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    block_number: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
    )

    contract_address: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    network: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
