from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class BoundarySchema(BaseModel):
    north: str = ""
    south: str = ""
    east: str = ""
    west: str = ""

class CoordinatePoint(BaseModel):
    lat: float
    lng: float

class LandRecordExtracted(BaseModel):
    survey_number: str
    district: str
    taluk: str
    village: str
    area_sqft: float
    area_sqm: Optional[float] = None
    boundaries: BoundarySchema
    owner_name_masked: str
    owner_hash: Optional[str] = None
    coordinates: List[List[float]] = []  # List of [lat, lng]

class PreprocessingResponse(BaseModel):
    steps_applied: List[str]
    is_deskewed: bool
    contrast_enhanced: bool
    noise_reduced: bool
    processed_image_path: Optional[str] = None

class OCRResponse(BaseModel):
    raw_text: str
    confidence_score: float
    extracted_fields: LandRecordExtracted
    extraction_method: str = "OCR + Domain Rule Engine"

class OverlapDetail(BaseModel):
    collision_detected: bool
    overlap_area_sqm: float = 0.0
    overlap_area_sqft: float = 0.0
    overlap_percentage: float = 0.0
    affected_surveys: List[str] = []
    risk_level: str = "NONE"  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    action_required: str = "Proceed"
    collision_polygon_geojson: Optional[Dict[str, Any]] = None

class SpatialAnalysisResponse(BaseModel):
    boundary_valid: bool
    area_consistent: bool
    overlap_detail: OverlapDetail
    submitted_plot_geojson: Dict[str, Any]
    cadastral_layer_geojson: Dict[str, Any]
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)

class TamperAnalysisResponse(BaseModel):
    is_authentic: bool
    is_tampered: bool
    document_hash: str
    registered_hash: Optional[str] = None
    mismatched_fields: List[str] = []
    tamper_type: Optional[str] = None
    tamper_severity: str = "NONE"

class PrivacyProofResponse(BaseModel):
    pii_redacted: bool
    citizen_identity_verified: bool
    ownership_commitment_hash: str
    zk_proof_status: str = "VALID (Pedersen Commitment Verified)"
    exposed_pii_fields: List[str] = []

class BlockchainVerificationResponse(BaseModel):
    registered_on_chain: bool
    document_hash: str
    verification_id: str
    transaction_hash: str
    block_number: int
    contract_address: str
    network: str
    timestamp: str
    block_explorer_url: str

class FullVerificationResponse(BaseModel):
    verification_id: str
    document_id: int
    overall_status: str  # VERIFIED, SPATIAL_COLLISION, TAMPER_ALERT, MANUAL_REVIEW
    confidence_score: float
    created_at: datetime
    document: Dict[str, Any]
    spatial: SpatialAnalysisResponse
    authenticity: TamperAnalysisResponse
    privacy: PrivacyProofResponse
    blockchain: BlockchainVerificationResponse
    certificate_url: Optional[str] = None
    qr_code_url: Optional[str] = None

class DocumentUploadResponse(BaseModel):
    document_id: int
    verification_id: str
    file_name: str
    file_hash: str
    file_size: int
    preview_url: str

class PublicVerifyResponse(BaseModel):
    document_hash: str
    verification_id: str
    status: str
    survey_number: str
    district: str
    taluk: str
    village: str
    area_sqft: float
    is_tampered: bool
    blockchain_tx: str
    block_number: int
    registration_timestamp: str
    certificate_url: Optional[str] = None
