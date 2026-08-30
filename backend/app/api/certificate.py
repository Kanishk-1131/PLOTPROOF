import os
from typing import Any, Dict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.certificate import Certificate
from app.services.document_service import DocumentService
from app.services.certificate_service import CertificateService
from app.schemas.certificate import (
    CertificateResponse,
    CertificateRevokeRequest,
    CertificateIntegrityCheckResponse,
    PublicVerificationPortalResponse,
)

router = APIRouter(tags=["Certificate & Public Verification"])

cert_service = CertificateService()
doc_service = DocumentService()


@router.post(
    "/api/v1/documents/{document_id}/certificate",
    response_model=CertificateResponse,
)
def generate_certificate_endpoint(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generates a tamper-evident verification certificate PDF (Section 9, 10, & 13).
    Enforces prerequisite validation: Integrity PASS, GIS PASS, ZK VALID, Blockchain CONFIRMED.
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return cert_service.generate_certificate(db=db, document_id=doc.id, actor_id=current_user.id)


@router.get(
    "/api/v1/documents/{document_id}/certificate",
    response_model=CertificateResponse,
)
def get_certificate_endpoint(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves certificate metadata for a document (Section 13).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return cert_service.get_certificate(db=db, document_id=doc.id)


@router.get(
    "/api/v1/certificates/{certificate_id}/download",
)
def download_certificate_endpoint(
    certificate_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Access-controlled certificate PDF download endpoint (Section 23).
    """
    cert = db.scalar(select(Certificate).where(Certificate.id == certificate_id))
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    # Authorize caller
    doc = doc_service.get_document_with_auth(db=db, document_id=cert.document_id, user=current_user)
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="Certificate PDF file not found in storage")

    return FileResponse(
        path=cert.file_path,
        filename=f"{cert.certificate_number}.pdf",
        media_type="application/pdf",
    )


@router.post(
    "/api/v1/certificates/{certificate_id}/revoke",
)
def revoke_certificate_endpoint(
    certificate_id: int,
    request: CertificateRevokeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Revokes a certificate (Section 18 & 28). Restricted to Registrar and Admin roles.
    """
    return cert_service.revoke_certificate(
        db=db,
        certificate_id=certificate_id,
        reason=request.reason,
        actor=current_user,
    )


@router.post(
    "/api/v1/certificates/{certificate_number}/verify-integrity",
    response_model=CertificateIntegrityCheckResponse,
)
async def verify_certificate_file_integrity_endpoint(
    certificate_number: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Verifies SHA-256 integrity of a presented certificate PDF file against stored hash (Section 24).
    """
    content = await file.read()
    return cert_service.verify_certificate_integrity(
        db=db,
        certificate_number=certificate_number,
        presented_pdf_bytes=content,
    )


@router.get(
    "/api/v1/public/verify/{verification_id}",
    response_model=PublicVerificationPortalResponse,
)
def public_verify_endpoint(
    verification_id: str,
    db: Session = Depends(get_db),
):
    """
    Public verification endpoint queried by QR code scanners and verifiers (Section 14 & 15).
    Strictly omits citizen PII and cross-checks Polygon blockchain state.
    """
    return cert_service.get_public_verification_portal_data(db=db, verification_id=verification_id)


@router.get(
    "/api/v1/verification/{verification_id}/certificate",
    response_model=CertificateResponse,
)
def get_certificate_by_verification_id_endpoint(
    verification_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves certificate metadata by verification ID (Section 13).
    """
    return cert_service.get_certificate_by_verification_id(db=db, verification_id=verification_id)
