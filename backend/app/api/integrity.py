from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.integrity import (
    IntegrityResponse,
    IntegrityVerifyResponse,
    PublicVerificationResponse,
)
from app.services.integrity_service import IntegrityService
from app.services.document_service import DocumentService

router = APIRouter(tags=["Integrity & Cryptographic Verification"])

integrity_service = IntegrityService()
doc_service = DocumentService()


@router.post(
    "/api/v1/documents/{document_id}/integrity/generate",
    response_model=IntegrityResponse,
)
def generate_integrity(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates or refreshes the multi-stage cryptographic integrity chain (Section 18).
    Links File Hash + OCR Hash + Metadata Hash + Spatial Hash -> Verification Hash.
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return integrity_service.generate_document_integrity(
        db=db,
        document_id=doc.id,
        actor_id=current_user.id,
    )


@router.get(
    "/api/v1/documents/{document_id}/integrity",
    response_model=IntegrityResponse,
)
def get_integrity(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves the cryptographic integrity record and verification status (Section 18).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return integrity_service.generate_document_integrity(
        db=db,
        document_id=doc.id,
        actor_id=current_user.id,
    )


@router.post(
    "/api/v1/documents/{document_id}/integrity/verify",
    response_model=IntegrityVerifyResponse,
)
async def verify_document_integrity_endpoint(
    document_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verifies byte-for-byte fidelity of a presented file against stored hash (Section 18).
    Returns MATCH or MISMATCH.
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    contents = await file.read()
    return integrity_service.verify_presented_file(
        db=db,
        document_id=doc.id,
        presented_bytes=contents,
        actor_id=current_user.id,
    )


@router.get(
    "/api/v1/verify/public/{verification_id}",
    response_model=PublicVerificationResponse,
)
def get_public_verification_endpoint(
    verification_id: str,
    db: Session = Depends(get_db),
):
    """
    Public QR verification endpoint accessible by banks, citizens, and registrars (Section 19).
    Exposes only non-sensitive verification status; never reveals citizen Aadhaar, phone, or raw deed.
    """
    return integrity_service.get_public_verification(
        db=db,
        verification_id=verification_id,
    )
