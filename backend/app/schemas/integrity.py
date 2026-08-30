from typing import Any, Dict, Optional
from pydantic import BaseModel


class IntegrityHashes(BaseModel):
    file_hash: str
    ocr_hash: Optional[str] = None
    metadata_hash: Optional[str] = None
    spatial_hash: Optional[str] = None
    verification_hash: Optional[str] = None


class IntegrityAudit(BaseModel):
    version: int = 1
    algorithm_version: str = "integrity-1.0.0"


class IntegrityResponse(BaseModel):
    document_id: int
    integrity: IntegrityHashes
    status: str
    audit: IntegrityAudit


class IntegrityVerifyResponse(BaseModel):
    document_id: int
    integrity: str  # "MATCH" or "MISMATCH"
    stored_hash: str
    computed_hash: str
    is_valid: bool


class PublicVerificationResponse(BaseModel):
    verification_id: str
    status: str
    survey_reference: str
    spatial_check: str
    integrity: str
    verification_date: str
    blockchain_anchor: str
