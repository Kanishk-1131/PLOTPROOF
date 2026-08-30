from typing import Optional
from pydantic import BaseModel


class CertificateResponse(BaseModel):
    certificate_number: str
    verification_id: str
    document_id: int
    certificate_hash: str
    status: str
    created_at: str
    download_url: str
    verification_url: str


class CertificateRevokeRequest(BaseModel):
    reason: str


class CertificateIntegrityCheckResponse(BaseModel):
    certificate_number: str
    is_valid: bool
    current_hash: str
    stored_hash: str
    status: str
    message: str


class PublicVerificationPortalResponse(BaseModel):
    verification_id: str
    status: str
    document_integrity: str
    spatial_validation: str
    privacy_proof: str
    blockchain_anchor: str
    verification_date: str
    network: str
    blockchain_transaction_hash: Optional[str] = None
    certificate_number: Optional[str] = None
    certificate_hash: Optional[str] = None
    block_explorer_url: Optional[str] = None
    disclaimer: str
