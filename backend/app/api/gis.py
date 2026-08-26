from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.database.connection import get_db
from app.services.gis_service import GISService
from pydantic import BaseModel

router = APIRouter(prefix="/api/gis", tags=["GIS Intelligence"])

class SpatialCheckRequest(BaseModel):
    survey_number: str
    coordinates: List[List[float]]
    area_sqft: float

@router.get("/cadastral-layer")
async def get_cadastral_layer(db: Session = Depends(get_db)):
    """
    Returns all registered cadastral parcels in GeoJSON format.
    """
    return GISService.get_cadastral_layer(db)

@router.post("/check-overlap")
async def check_overlap(req: SpatialCheckRequest, db: Session = Depends(get_db)):
    """
    Performs spatial collision and overlap computation.
    """
    return GISService.check_spatial_collision(
        db=db,
        submitted_survey=req.survey_number,
        coordinates=req.coordinates,
        claimed_area_sqft=req.area_sqft
    )
