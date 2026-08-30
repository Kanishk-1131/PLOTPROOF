from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database.base import Base


class Verification(Base):
    """
    Central Verification Entity connecting Document, OCR, GIS, Integrity, ZK, Blockchain,
    Certificate, and Forensic Audit Records (Layer 11, Section 2 & 3).
    Supports both Layer 11 Central Orchestration State Machine and legacy score reporting.
    """
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), unique=True, index=True, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Central Orchestration State Machine (Layer 11, Section 1)
    status = Column(String(50), default="UPLOADED", nullable=False, index=True)
    current_stage = Column(String(50), default="DOCUMENT", nullable=False)
    stages_json = Column(
        JSON,
        nullable=False,
        default=lambda: {
            "document": "COMPLETED",
            "ocr": "PENDING",
            "gis": "PENDING",
            "integrity": "PENDING",
            "fraud": "PENDING",
            "zk": "PENDING",
            "blockchain": "PENDING",
            "certificate": "PENDING",
        },
    )
    error_message = Column(Text, nullable=True)

    # Forensic Multi-Vector Scores (Layer 1 compatibility)
    ocr_score = Column(Float, default=0.0)
    spatial_score = Column(Float, default=0.0)
    authenticity_score = Column(Float, default=0.0)
    privacy_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    # Collision & Tamper flags
    collision_detected = Column(Boolean, default=False)
    tamper_detected = Column(Boolean, default=False)
    collision_details_json = Column(Text, nullable=True)
    tamper_details_json = Column(Text, nullable=True)
    privacy_details_json = Column(Text, nullable=True)

    # Generated Artifacts
    certificate_url = Column(String(500), nullable=True)
    qr_code_url = Column(String(500), nullable=True)

    # Statutory Human Review Workflow (Layer 11, Section 11 & 12)
    review_required = Column(Boolean, default=False, nullable=False)
    review_reason = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_decision = Column(String(30), nullable=True)  # "APPROVED" or "REJECTED"

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="verification")
    blockchain_record = relationship("BlockchainRecord", back_populates="verification", uselist=False)


# Backward compatibility alias
VerificationRecord = Verification
