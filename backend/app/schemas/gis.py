from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class ParcelResponse(BaseModel):
    id: int
    survey_number: str
    district: str
    taluk: str
    village: str
    area_sq_m: float
    geojson: Dict[str, Any]

    model_config = {"from_attributes": True}


class SpatialValidationResponse(BaseModel):
    document_id: int
    parcel: Dict[str, Any]
    geometry: Dict[str, Any]
    spatial_relationship: Dict[str, Any]
    area_validation: Dict[str, Any]
    risk: Dict[str, Any]
    decision: str


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    properties: Dict[str, Any]
    geometry: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]
