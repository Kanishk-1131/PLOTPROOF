from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class CommitmentResponse(BaseModel):
    document_id: int
    commitment_id: str
    commitment: str
    status: str = "CREATED"


class ZKProofGenerateResponse(BaseModel):
    document_id: int
    proof_id: str
    commitment: str
    circuit_version: str
    verification_key_version: str
    status: str
    public_signals: List[str]


class ZKProofVerifyResponse(BaseModel):
    proof_id: str
    is_valid: bool
    status: str
    verified_at: str


class PrivacyStatusResponse(BaseModel):
    document_id: int
    private_identity: str = "PROTECTED"
    commitment: str = "CREATED"
    zk_proof: str = "VERIFIED"
    sensitive_data_exposed: str = "NO"
    proof_id: Optional[str] = None


class ZKBlockchainHandshakePayload(BaseModel):
    verification_id: str
    verification_hash: str
    commitment: str
    zk_proof: Dict[str, Any]
    public_signals: List[str]
    circuit_version: str = "land-verification-v1"
    status: str = "ZK_VERIFIED"
