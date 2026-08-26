from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base
from app.models.user import User, UserRole

from app.models.document import Document, DocumentStatus


class LandRecord(Base):
    __tablename__ = "land_records"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    survey_number = Column(String(100), index=True, nullable=False)
    district = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=False)
    village = Column(String(100), nullable=False)
    area_sqft = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=True)
    owner_name_masked = Column(String(255), nullable=True)
    owner_hash = Column(String(64), nullable=True)
    boundary_north = Column(String(255), nullable=True)
    boundary_south = Column(String(255), nullable=True)
    boundary_east = Column(String(255), nullable=True)
    boundary_west = Column(String(255), nullable=True)
    coordinates_json = Column(Text, nullable=True)  # List of [lat, lng]
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="land_record")

class Plot(Base):
    __tablename__ = "plots"

    id = Column(Integer, primary_key=True, index=True)
    plot_id = Column(String(100), unique=True, index=True, nullable=False)
    survey_number = Column(String(100), index=True, nullable=False)
    village = Column(String(100), nullable=False)
    taluk = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    area_sqft = Column(Float, nullable=False)
    area_sqm = Column(Float, nullable=True)
    geometry_wkt = Column(Text, nullable=False)  # POLYGON(...)
    geometry_geojson = Column(Text, nullable=True)  # GeoJSON Polygon
    owner_name_masked = Column(String(255), default="REDACTED (GOVT TITLE)")
    status = Column(String(50), default="REGISTERED")  # REGISTERED, DISPUTED, ENCROACHED
    created_at = Column(DateTime, default=datetime.utcnow)

from app.models.verification import Verification, VerificationRecord


class BlockchainRecord(Base):
    __tablename__ = "blockchain_records"

    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(100), ForeignKey("verifications.verification_id"), unique=True, nullable=False)
    document_hash = Column(String(64), index=True, nullable=False)
    transaction_hash = Column(String(66), nullable=False)
    block_number = Column(Integer, default=1)
    contract_address = Column(String(42), default="0x71C8366420A0926718E29ce7705B732d43b91B32")
    network = Column(String(50), default="Polygon Amoy / Local Testnet")
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="CONFIRMED")

    verification = relationship("Verification", back_populates="blockchain_record")
