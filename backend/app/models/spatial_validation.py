from datetime import datetime
from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class SpatialValidation(Base):
    __tablename__ = "spatial_validations"

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
        index=True,
    )

    parcel_id: Mapped[int | None] = mapped_column(
        ForeignKey("parcels.id"),
        nullable=True,
    )

    geometry_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    overlap_detected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    overlap_area_sq_m: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    overlap_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    area_difference_percent: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    spatial_relationship: Mapped[str] = mapped_column(
        String(50),
        default="DISJOINT",
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    algorithm_version: Mapped[str] = mapped_column(
        String(50),
        default="gis-1.0.0",
        nullable=False,
    )

    dataset_version: Mapped[str] = mapped_column(
        String(50),
        default="cadastral-2026-08",
        nullable=False,
    )

    crs: Mapped[str] = mapped_column(
        String(50),
        default="EPSG:4326",
        nullable=False,
    )

    candidate_geojson: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    details_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    document = relationship("Document", backref="spatial_validations")
    parcel = relationship("Parcel", backref="spatial_validations")
