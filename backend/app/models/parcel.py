from datetime import datetime
from typing import Any
from sqlalchemy import (
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeDecorator
from geoalchemy2 import Geometry, WKTElement
from shapely.geometry import Polygon
from shapely import wkt

from app.database.base import Base


class CompatibleGeometry(TypeDecorator):
    """
    Database-agnostic geometry type.
    Uses native PostGIS Geometry on PostgreSQL and WKT text representation on SQLite.
    """
    impl = Text
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Geometry(geometry_type="POLYGON", srid=4326))
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, Polygon):
            wkt_str = value.wkt
        elif hasattr(value, "desc"):
            wkt_str = str(value.desc)
        else:
            wkt_str = str(value)

        if dialect.name == "postgresql":
            return WKTElement(wkt_str, srid=4326)
        return wkt_str

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return str(value)


class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    survey_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    taluk: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    village: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    area_sq_m: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    geometry = mapped_column(
        CompatibleGeometry(),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
        nullable=False,
    )

    def to_shapely(self) -> Polygon:
        """Returns the geometry as a Shapely Polygon."""
        geom_str = str(self.geometry)
        if geom_str.startswith("0103") or geom_str.startswith("0000"):
            # WKB hex string
            from shapely import wkb
            return wkb.loads(bytes.fromhex(geom_str))
        return wkt.loads(geom_str)
