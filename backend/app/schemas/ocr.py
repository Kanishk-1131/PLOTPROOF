from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class OCRFieldItem(BaseModel):
    id: int
    field_name: str
    field_value: Optional[str] = None
    confidence: float
    status: str
    source_text: Optional[str] = None
    page_number: Optional[int] = None
    tier: str = "HIGH"

    model_config = {"from_attributes": True}


class OCRFieldUpdateRequest(BaseModel):
    field_value: str
    status: str = "CORRECTED"  # CONFIRMED, CORRECTED, REJECTED


class OCRDocumentResultResponse(BaseModel):
    document_id: int
    engine: str
    full_text: str
    raw_blocks: List[Dict[str, Any]]
    fields: List[OCRFieldItem]
    overall_confidence: float
    review_required: bool


class Layer5HandshakePayload(BaseModel):
    document_id: int
    land: Dict[str, Any]
    boundaries: Dict[str, str]
    coordinates: Dict[str, float]
    quality: Dict[str, Any]
