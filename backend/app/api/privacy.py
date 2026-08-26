from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.zk import (
    CommitmentResponse,
    ZKProofGenerateResponse,
    ZKProofVerifyResponse,
    PrivacyStatusResponse,
)
from app.services.document_service import DocumentService
from app.privacy.zk_service import ZKService

router = APIRouter(tags=["Privacy & Zero-Knowledge Proofs"])

zk_service = ZKService()
doc_service = DocumentService()


@router.post(
    "/api/v1/documents/{document_id}/privacy/commit",
    response_model=CommitmentResponse,
)
def create_commitment_endpoint(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Creates a Poseidon cryptographic commitment over private record and random salt (Section 17).
    Never exposes or returns the private secret to callers.
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return zk_service.create_commitment(db=db, document_id=doc.id, actor_id=current_user.id)


@router.post(
    "/api/v1/documents/{document_id}/privacy/prove",
    response_model=ZKProofGenerateResponse,
)
def generate_proof_endpoint(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates Groth16 Zero-Knowledge Proof verifying statutory correctness without exposing citizen PII (Section 18).
    Enforces prerequisite validation: Integrity PASS, GIS PASS, and Status APPROVED.
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return zk_service.generate_proof(db=db, document_id=doc.id, actor_id=current_user.id)


@router.post(
    "/api/v1/documents/{document_id}/privacy/verify",
    response_model=ZKProofVerifyResponse,
)
def verify_proof_endpoint(
    document_id: int,
    proof_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Locally verifies an existing ZK proof against verification key and public signals (Section 15 & 22).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return zk_service.verify_proof(db=db, proof_id=proof_id, actor_id=current_user.id)


@router.get(
    "/api/v1/documents/{document_id}/privacy/status",
    response_model=PrivacyStatusResponse,
)
def get_privacy_status_endpoint(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves privacy status summary showing private identity protection and proof readiness (Section 24).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return zk_service.get_privacy_status(db=db, document_id=doc.id)
