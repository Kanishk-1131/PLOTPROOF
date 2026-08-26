from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import BaseModel
from shapely.geometry import mapping

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.parcel import Parcel
from app.schemas.gis import (
    ParcelResponse,
    SpatialValidationResponse,
    GeoJSONFeatureCollection,
)
from app.services.gis_service import GISService
from app.services.document_service import DocumentService

router = APIRouter(tags=["GIS & Spatial Validation"])

gis_service = GISService()
doc_service = DocumentService()


# --- LAYER 5 REST ENDPOINTS (Section 23) ---

@router.post(
    "/api/v1/documents/{document_id}/spatial/validate",
    response_model=SpatialValidationResponse,
)
def validate_spatial(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes full Layer 5 GIS & Spatial Validation on a document (Section 23 & 29).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    handshake = gis_service.validate_document_spatial(db=db, document_id=doc.id)
    return SpatialValidationResponse(**handshake)


@router.get(
    "/api/v1/documents/{document_id}/spatial",
    response_model=SpatialValidationResponse,
)
def get_spatial_status(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves spatial validation results, relationship classification, and risk score (Section 23).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    handshake = gis_service.validate_document_spatial(db=db, document_id=doc.id)
    return SpatialValidationResponse(**handshake)


@router.get(
    "/api/v1/documents/{document_id}/spatial/map",
    response_model=GeoJSONFeatureCollection,
)
def get_spatial_map(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns privacy-isolated GeoJSON FeatureCollection for MapLibre / Leaflet map rendering (Section 24 & 26).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    geojson_data = gis_service.get_map_geojson(db=db, document_id=doc.id)
    return GeoJSONFeatureCollection(**geojson_data)


@router.get(
    "/api/v1/parcels/{parcel_id}",
    response_model=ParcelResponse,
)
def get_parcel(
    parcel_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves a single reference cadastral parcel by ID (Section 23).
    """
    parcel = db.scalar(select(Parcel).where(Parcel.id == parcel_id))
    if not parcel:
        raise HTTPException(status_code=404, detail="Parcel not found")

    return ParcelResponse(
        id=parcel.id,
        survey_number=parcel.survey_number,
        district=parcel.district,
        taluk=parcel.taluk,
        village=parcel.village,
        area_sq_m=parcel.area_sq_m,
        geojson=mapping(parcel.to_shapely()),
    )


# --- LEGACY ENDPOINTS (Layer 1 Backwards Compatibility) ---

class SpatialCheckRequest(BaseModel):
    survey_number: str
    coordinates: List[List[float]]
    area_sqft: float


@router.get("/api/gis/cadastral-layer")
def get_cadastral_layer_legacy(db: Session = Depends(get_db)):
    """
    Returns registered cadastral parcels in GeoJSON format for the interactive map.
    """
    return GISService.get_cadastral_layer(db)


@router.post("/api/gis/check-overlap")
def check_overlap_legacy(req: SpatialCheckRequest, db: Session = Depends(get_db)):
    """
    Legacy spatial collision checker.
    """
    return GISService.check_spatial_collision(
        db=db,
        submitted_survey=req.survey_number,
        coordinates=req.coordinates,
        claimed_area_sqft=req.area_sqft,
    )
