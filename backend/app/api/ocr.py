from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.ocr_field import OCRField
from app.models.user import User
from app.schemas.ocr import (
    OCRDocumentResultResponse,
    OCRFieldItem,
    OCRFieldUpdateRequest,
    Layer5HandshakePayload,
)
from app.services.ocr_service import OCRService
from app.services.document_service import DocumentService
from app.ocr.confidence import classify_confidence_tier

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["OCR & Document Intelligence"],
)

ocr_service = OCRService()
doc_service = DocumentService()


@router.get(
    "/{document_id}/ocr",
    response_model=OCRDocumentResultResponse,
)
def get_raw_ocr_result(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves full raw OCR text and bounding boxes for spatial inspection (Section 10 & 23).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)

    res = db.scalar(select(OCRResult).where(OCRResult.document_id == doc.id))
    if not res:
        # If not yet extracted, run extraction on demand
        handshake = ocr_service.process_document(db=db, document_id=doc.id)
        res = db.scalar(select(OCRResult).where(OCRResult.document_id == doc.id))

    fields = list(db.scalars(select(OCRField).where(OCRField.document_id == doc.id)).all())
    field_items = [
        OCRFieldItem(
            id=f.id,
            field_name=f.field_name,
            field_value=f.field_value,
            confidence=f.confidence,
            status=f.status,
            source_text=f.source_text,
            page_number=f.page_number,
            tier=classify_confidence_tier(f.confidence),
        )
        for f in fields
    ]

    conf_values = [f.confidence for f in fields]
    avg_conf = round(sum(conf_values) / len(conf_values), 3) if conf_values else 0.90
    review_req = any(f.status == "REVIEW_REQUIRED" for f in fields)

    return OCRDocumentResultResponse(
        document_id=doc.id,
        engine=res.engine,
        full_text=res.full_text,
        raw_blocks=res.raw_blocks,
        fields=field_items,
        overall_confidence=avg_conf,
        review_required=review_req,
    )


@router.get(
    "/{document_id}/fields",
    response_model=List[OCRFieldItem],
)
def get_extracted_fields(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves structured land title fields with confidence scoring and review flags (Section 20 & 23).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)

    fields = list(db.scalars(select(OCRField).where(OCRField.document_id == doc.id)).all())
    if not fields:
        ocr_service.process_document(db=db, document_id=doc.id)
        fields = list(db.scalars(select(OCRField).where(OCRField.document_id == doc.id)).all())

    return [
        OCRFieldItem(
            id=f.id,
            field_name=f.field_name,
            field_value=f.field_value,
            confidence=f.confidence,
            status=f.status,
            source_text=f.source_text,
            page_number=f.page_number,
            tier=classify_confidence_tier(f.confidence),
        )
        for f in fields
    ]


@router.patch(
    "/{document_id}/fields/{field_id}",
    response_model=OCRFieldItem,
)
def update_extracted_field(
    document_id: int,
    field_id: int,
    payload: OCRFieldUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Human Review statutory correction workflow for Sub-Registrars and Admins (Section 21 & 22).
    """
    client_ip = request.client.host if request.client else None
    updated = ocr_service.update_field(
        db=db,
        document_id=document_id,
        field_id=field_id,
        new_value=payload.field_value,
        new_status=payload.status,
        user=current_user,
        ip_address=client_ip,
    )
    return OCRFieldItem(
        id=updated.id,
        field_name=updated.field_name,
        field_value=updated.field_value,
        confidence=updated.confidence,
        status=updated.status,
        source_text=updated.source_text,
        page_number=updated.page_number,
        tier="HIGH",
    )


@router.post(
    "/{document_id}/ocr/reprocess",
    response_model=Layer5HandshakePayload,
)
def reprocess_ocr(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Forces full OCR and deterministic rule re-extraction (Section 23).
    """
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    handshake = ocr_service.process_document(db=db, document_id=doc.id)
    return Layer5HandshakePayload(**handshake)
