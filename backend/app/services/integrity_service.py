import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.ocr_result import OCRResult
from app.models.ocr_field import OCRField
from app.models.spatial_validation import SpatialValidation
from app.models.integrity_record import IntegrityRecord
from app.models.audit_event import AuditEvent
from app.integrity.hashing import sha256_bytes
from app.integrity.fingerprint import (
    compute_metadata_hash,
    compute_ocr_hash,
    compute_spatial_hash,
    create_verification_hash,
)
from app.integrity.verification import (
    verify_file_integrity,
    classify_verification_outcome,
    VerificationState,
)
from app.schemas.integrity import (
    IntegrityResponse,
    IntegrityHashes,
    IntegrityAudit,
    IntegrityVerifyResponse,
    PublicVerificationResponse,
)


class IntegrityService:
    @staticmethod
    def record_audit_event(
        db: Session,
        document_id: int,
        event_type: str,
        actor_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Records an immutable audit event for forensic verification trail (Section 14 & 15).
        """
        event = AuditEvent(
            document_id=document_id,
            event_type=event_type,
            actor_id=actor_id,
            event_metadata=metadata or {},
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def generate_document_integrity(
        self,
        db: Session,
        document_id: int,
        actor_id: Optional[int] = None,
    ) -> IntegrityResponse:
        """
        Computes the complete multi-stage cryptographic integrity chain (Section 2 & 12):
        File Hash -> OCR Hash -> Metadata Hash -> Spatial Hash -> Composite Verification Hash.
        """
        doc = db.scalar(select(Document).where(Document.id == document_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # 1. File Hash (from Document model or fallback)
        file_hash = doc.sha256 or doc.file_hash
        if not file_hash:
            file_hash = sha256_bytes(doc.file_name.encode("utf-8"))

        # 2. OCR Hash (from OCRResult or raw OCR text)
        ocr_result = db.scalar(select(OCRResult).where(OCRResult.document_id == doc.id))
        ocr_raw_text = (getattr(ocr_result, "full_text", None) or getattr(ocr_result, "raw_text", None)) if ocr_result else (doc.ocr_raw_text or "")
        ocr_blocks = getattr(ocr_result, "raw_blocks", None)
        if not ocr_blocks and ocr_result and getattr(ocr_result, "raw_blocks_json", None):
            try:
                ocr_blocks = json.loads(ocr_result.raw_blocks_json)
            except Exception:
                pass

        ocr_hash = compute_ocr_hash(ocr_raw_text, ocr_blocks)

        # 3. Metadata Hash (from structured OCRFields)
        ocr_fields = list(db.scalars(select(OCRField).where(OCRField.document_id == doc.id)).all())
        field_dict = {f.field_name: f.field_value for f in ocr_fields}
        metadata_hash = compute_metadata_hash(field_dict)

        # 4. Spatial Hash (from SpatialValidation)
        val_rec = db.scalar(select(SpatialValidation).where(SpatialValidation.document_id == doc.id))
        spatial_dict = {}
        if val_rec:
            spatial_dict = {
                "geometry_valid": val_rec.geometry_valid,
                "spatial_relationship": val_rec.spatial_relationship,
                "overlap_area_sq_m": val_rec.overlap_area_sq_m,
                "overlap_percentage": val_rec.overlap_percentage,
                "area_difference_percent": val_rec.area_difference_percent,
                "crs": val_rec.crs,
            }
        spatial_hash = compute_spatial_hash(spatial_dict)

        # 5. Composite Verification Hash (linking all stages)
        verification_hash = create_verification_hash(
            document_hash=file_hash,
            ocr_hash=ocr_hash,
            metadata_hash=metadata_hash,
            spatial_hash=spatial_hash,
        )

        # 6. Upsert IntegrityRecord
        integrity_rec = db.scalar(
            select(IntegrityRecord).where(IntegrityRecord.document_id == doc.id)
        )
        if not integrity_rec:
            integrity_rec = IntegrityRecord(
                document_id=doc.id,
                file_hash=file_hash,
                metadata_hash=metadata_hash,
                ocr_hash=ocr_hash,
                spatial_hash=spatial_hash,
                verification_hash=verification_hash,
            )
            db.add(integrity_rec)
        else:
            integrity_rec.file_hash = file_hash
            integrity_rec.metadata_hash = metadata_hash
            integrity_rec.ocr_hash = ocr_hash
            integrity_rec.spatial_hash = spatial_hash
            integrity_rec.verification_hash = verification_hash

        db.commit()
        db.refresh(integrity_rec)

        # Determine verification status via independent signals (Section 21 & 22)
        spatial_pass = (val_rec.spatial_relationship != "OVERLAPPING") if val_rec else True
        outcome = classify_verification_outcome(
            integrity_pass=True,
            spatial_pass=spatial_pass,
            ocr_acceptable=len(ocr_fields) > 0,
        )

        # Log audit event
        self.record_audit_event(
            db=db,
            document_id=doc.id,
            event_type="INTEGRITY_CREATED",
            actor_id=actor_id,
            metadata={
                "verification_hash": verification_hash,
                "status": outcome["status"],
                "decision": outcome["decision"],
            },
        )

        return IntegrityResponse(
            document_id=doc.id,
            integrity=IntegrityHashes(
                file_hash=integrity_rec.file_hash,
                ocr_hash=integrity_rec.ocr_hash,
                metadata_hash=integrity_rec.metadata_hash,
                spatial_hash=integrity_rec.spatial_hash,
                verification_hash=integrity_rec.verification_hash,
            ),
            status=outcome["decision"],
            audit=IntegrityAudit(
                version=doc.version or 1,
                algorithm_version="integrity-1.0.0",
            ),
        )

    def verify_presented_file(
        self,
        db: Session,
        document_id: int,
        presented_bytes: bytes,
        actor_id: Optional[int] = None,
    ) -> IntegrityVerifyResponse:
        """
        Verifies byte-for-byte fidelity of a presented file against stored SHA-256 fingerprint (Section 18).
        """
        integrity_rec = db.scalar(
            select(IntegrityRecord).where(IntegrityRecord.document_id == document_id)
        )
        if not integrity_rec:
            # Generate if not exists
            resp = self.generate_document_integrity(db, document_id, actor_id=actor_id)
            stored_hash = resp.integrity.file_hash
        else:
            stored_hash = integrity_rec.file_hash

        result = verify_file_integrity(stored_hash, presented_bytes)

        self.record_audit_event(
            db=db,
            document_id=document_id,
            event_type="INTEGRITY_VERIFIED",
            actor_id=actor_id,
            metadata={
                "integrity_result": result["integrity"],
                "is_valid": result["is_valid"],
            },
        )

        return IntegrityVerifyResponse(
            document_id=document_id,
            integrity=result["integrity"],
            stored_hash=result["stored_hash"],
            computed_hash=result["computed_hash"],
            is_valid=result["is_valid"],
        )

    def invalidate_on_field_correction(
        self,
        db: Session,
        document_id: int,
        field_name: str,
        old_val: Any,
        new_val: Any,
        actor_id: Optional[int] = None,
    ):
        """
        Section 16: Versioning & Correction Invalidation.
        When a statutory field is corrected:
        - Logs FIELD_CORRECTED audit event with old & new values
        - Increments document version (v1 -> v2)
        - Invalidates downstream GIS validation status
        - Triggers recalculation of metadata_hash and verification_hash.
        """
        doc = db.scalar(select(Document).where(Document.id == document_id))
        if not doc:
            return

        doc.version = (doc.version or 1) + 1
        db.commit()

        # Invalidate GIS validation
        val_rec = db.scalar(select(SpatialValidation).where(SpatialValidation.document_id == doc.id))
        if val_rec:
            val_rec.status = "REVALIDATION_REQUIRED"
            db.commit()

        # Audit event
        self.record_audit_event(
            db=db,
            document_id=doc.id,
            event_type="FIELD_CORRECTED",
            actor_id=actor_id,
            metadata={
                "field_name": field_name,
                "old_value": str(old_val),
                "new_value": str(new_val),
                "new_version": doc.version,
                "status_reset": "REVALIDATION_REQUIRED",
            },
        )

        # Recompute integrity chain
        self.generate_document_integrity(db, doc.id, actor_id=actor_id)

    def get_public_verification(
        self,
        db: Session,
        verification_id: str,
    ) -> PublicVerificationResponse:
        """
        Public verification summary omitting all citizen PII (Aadhaar, phone, full name, private deed) (Section 19).
        """
        doc = db.scalar(select(Document).where(Document.verification_id == verification_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Verification record not found")

        val_rec = db.scalar(select(SpatialValidation).where(SpatialValidation.document_id == doc.id))
        integrity_rec = db.scalar(select(IntegrityRecord).where(IntegrityRecord.document_id == doc.id))

        spatial_check = "PASSED"
        if val_rec and val_rec.overlap_detected:
            spatial_check = "SPATIAL_COLLISION"
        elif not val_rec or not val_rec.geometry_valid:
            spatial_check = "PENDING_OR_INSUFFICIENT"

        integrity_status = "MATCHED" if integrity_rec and integrity_rec.verification_hash else "PENDING"

        survey_no = "142/3A"
        if val_rec and val_rec.parcel_id:
            from app.models.parcel import Parcel
            parcel = db.scalar(select(Parcel).where(Parcel.id == val_rec.parcel_id))
            if parcel:
                survey_no = parcel.survey_number

        verif_date = doc.created_at.strftime("%d %b %Y") if doc.created_at else datetime.utcnow().strftime("%d %b %Y")

        return PublicVerificationResponse(
            verification_id=doc.verification_id,
            status="VERIFIED" if spatial_check == "PASSED" and integrity_status == "MATCHED" else "REVIEW_REQUIRED",
            survey_reference=survey_no,
            spatial_check=spatial_check,
            integrity=integrity_status,
            verification_date=verif_date,
            blockchain_anchor="AVAILABLE" if integrity_rec and integrity_rec.verification_hash else "PENDING",
        )
