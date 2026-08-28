from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

from app.schemas.document import DocumentUploadResponse


class UploadResponse(BaseModel):
    document_id: int
    verification_id: str
    file_name: str
    file_hash: str
    file_size: int
    preview_url: str



class FullVerificationResponse(BaseModel):
    class Config:
        extra = "allow"



class StartVerificationRequest(BaseModel):
    document_id: int


class ReviewDecisionRequest(BaseModel):
    decision: str = Field(..., description="'APPROVE' or 'REJECT'")
    notes: Optional[str] = None


class VerificationStageProgress(BaseModel):
    document: str = "PENDING"
    ocr: str = "PENDING"
    gis: str = "PENDING"
    integrity: str = "PENDING"
    fraud: str = "PENDING"
    zk: str = "PENDING"
    blockchain: str = "PENDING"
    certificate: str = "PENDING"


class VerificationStatusResponse(BaseModel):
    verification_id: str
    document_id: int
    status: str
    current_stage: str
    stages: Dict[str, Any]
    review_required: bool = False
    review_reason: Optional[str] = None
    review_decision: Optional[str] = None
    error_message: Optional[str] = None

    # Full integration sub-objects (Section 14)
    document: Optional[Dict[str, Any]] = None
    ocr: Optional[Dict[str, Any]] = None
    gis: Optional[Dict[str, Any]] = None
    integrity: Optional[Dict[str, Any]] = None
    fraud: Optional[Dict[str, Any]] = None
    zk: Optional[Dict[str, Any]] = None
    blockchain: Optional[Dict[str, Any]] = None
    certificate: Optional[Dict[str, Any]] = None

    created_at: str
    updated_at: str
