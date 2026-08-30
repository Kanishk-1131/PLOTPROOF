from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.orchestrator import OrchestratorService
from app.services.document_service import DocumentService
from app.schemas.verification import (
    StartVerificationRequest,
    ReviewDecisionRequest,
    VerificationStatusResponse,
)

router = APIRouter(
    prefix="/api/v1/verifications",
    tags=["End-to-End Orchestration"],
)

orchestrator = OrchestratorService()
doc_service = DocumentService()


@router.post(
    "",
    response_model=VerificationStatusResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_verification_endpoint(
    payload: StartVerificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Starts the full end-to-end verification orchestration workflow (Layer 11, Section 4).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=payload.document_id, user=current_user)
    verif = orchestrator.start_verification(db=db, document_id=doc.id, actor_id=current_user.id)
    return orchestrator.get_verification_full_status(db=db, verification_id=verif.verification_id)


@router.get(
    "/{verification_id}",
    response_model=VerificationStatusResponse,
)
def get_verification_status_endpoint(
    verification_id: str,
    db: Session = Depends(get_db),
):
    """
    Retrieves live stage-by-stage progression tracking (Layer 11, Section 5 & 14).
    """
    return orchestrator.get_verification_full_status(db=db, verification_id=verification_id)


@router.post(
    "/{verification_id}/retry",
    response_model=VerificationStatusResponse,
)
def retry_verification_endpoint(
    verification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Resumes pipeline from stalled or failed stage without losing progress (Layer 11, Section 8 & 10).
    """
    verif = orchestrator.process_verification(db=db, verification_id=verification_id, actor_id=current_user.id)
    return orchestrator.get_verification_full_status(db=db, verification_id=verif.verification_id)


@router.post(
    "/{verification_id}/review",
    response_model=VerificationStatusResponse,
)
def review_verification_endpoint(
    verification_id: str,
    payload: ReviewDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Records Sub-Registrar statutory review decision (Layer 11, Section 11 & 12).
    """
    verif = orchestrator.handle_review_decision(
        db=db,
        verification_id=verification_id,
        decision=payload.decision,
        notes=payload.notes,
        actor=current_user,
    )
    return orchestrator.get_verification_full_status(db=db, verification_id=verif.verification_id)


@router.get("/{verification_id}/report/docx")
def download_v1_docx_report(
    verification_id: str,
    db: Session = Depends(get_db),
):
    """
    Downloads the forensic audit report as a Microsoft Word (.docx) document.
    """
    from fastapi.responses import StreamingResponse
    from app.services.report_document_service import ReportDocumentService

    report_data = orchestrator.build_frontend_report(db, verification_id)
    docx_buffer = ReportDocumentService.generate_docx_report(report_data)
    filename = f"PlotProof_Forensic_Audit_{verification_id}.docx"

    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
