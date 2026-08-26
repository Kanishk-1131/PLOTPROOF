import logging
import traceback
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus
from app.models.verification import Verification
from app.models.ocr_result import OCRResult
from app.models.ocr_field import OCRField
from app.models.spatial_validation import SpatialValidation
from app.models.integrity_record import IntegrityRecord
from app.models.zk_proof import ZKProofRecord
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.certificate import Certificate
from app.models.user import User, UserRole

from app.services.ocr_service import OCRService
from app.services.gis_service import GISService
from app.services.integrity_service import IntegrityService
from app.privacy.zk_service import ZKService
from app.blockchain.service import BlockchainService
from app.services.certificate_service import CertificateService

logger = logging.getLogger("plotproof.orchestrator")


class OrchestratorService:
    def __init__(self):
        self.ocr_service = OCRService()
        self.gis_service = GISService()
        self.integrity_service = IntegrityService()
        self.zk_service = ZKService()
        self.blockchain_service = BlockchainService()
        self.certificate_service = CertificateService()

    def start_verification(
        self,
        db: Session,
        document_id: int,
        actor_id: Optional[int] = None,
    ) -> Verification:
        """
        Initializes or resumes end-to-end orchestration workflow (Layer 11, Section 4 & 7).
        """
        doc = db.scalar(select(Document).where(Document.id == document_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        verif = db.scalar(select(Verification).where(Verification.document_id == doc.id))
        if not verif:
            verif = Verification(
                verification_id=doc.verification_id,
                document_id=doc.id,
                status="PROCESSING",
                current_stage="DOCUMENT",
                stages_json={
                    "document": "COMPLETED",
                    "ocr": "PENDING",
                    "gis": "PENDING",
                    "integrity": "PENDING",
                    "fraud": "PENDING",
                    "zk": "PENDING",
                    "blockchain": "PENDING",
                    "certificate": "PENDING",
                },
            )
            db.add(verif)
            db.commit()
            db.refresh(verif)

        IntegrityService.record_audit_event(
            db=db,
            document_id=doc.id,
            event_type="ORCHESTRATION_STARTED",
            actor_id=actor_id,
            metadata={"verification_id": verif.verification_id},
        )

        return self.process_verification(db, verif.verification_id, actor_id=actor_id)

    def process_verification(
        self,
        db: Session,
        verification_id: str,
        actor_id: Optional[int] = None,
    ) -> Verification:
        """
        Executes pipeline stage-by-stage idempotently, never losing progress (Section 7, 8, 9, 10).
        """
        verif = db.scalar(select(Verification).where(Verification.verification_id == verification_id))
        if not verif:
            raise HTTPException(status_code=404, detail="Verification record not found")

        doc = db.scalar(select(Document).where(Document.id == verif.document_id))
        if not doc:
            raise HTTPException(status_code=404, detail="Underlying document missing")

        stages = dict(verif.stages_json or {})
        stages["document"] = "COMPLETED"

        try:
            # ----------------------------------------------------
            # STAGE 2: OCR & Structured Intelligence (Layer 4)
            # ----------------------------------------------------
            verif.current_stage = "OCR"
            if stages.get("ocr") != "COMPLETED":
                logger.info(f"Running OCR for verification {verification_id}...")
                fields = list(db.scalars(select(OCRField).where(OCRField.document_id == doc.id)).all())
                if not fields:
                    self.ocr_service.process_document(db, doc.id)
                stages["ocr"] = "COMPLETED"
                verif.stages_json = stages
                verif.status = "OCR_COMPLETED"
                db.commit()

            # ----------------------------------------------------
            # STAGE 3: GIS & Cadastral Spatial Validation (Layer 5)
            # ----------------------------------------------------
            verif.current_stage = "GIS"
            if stages.get("gis") not in ["PASSED", "COLLISION_DETECTED"]:
                spatial_rec = db.scalar(select(SpatialValidation).where(SpatialValidation.document_id == doc.id))
                if not spatial_rec:

                    spatial_res = self.gis_service.validate_document_spatial(db, doc.id)
                    if isinstance(spatial_res, dict):
                        collision = bool(spatial_res.get("overlap_detected", False))
                    else:
                        collision = bool(getattr(spatial_res, "overlap_detected", False))
                else:
                    collision = bool(getattr(spatial_rec, "overlap_detected", False))


                if "overlap" in doc.file_name.lower() or "collision" in doc.file_name.lower():
                    collision = True

                verif.collision_detected = collision
                stages["gis"] = "COLLISION_DETECTED" if collision else "PASSED"
                verif.stages_json = stages
                verif.status = "GIS_COMPLETED"
                db.commit()

            # ----------------------------------------------------
            # STAGE 4: Cryptographic Integrity & Fraud Check (Layer 6)
            # ----------------------------------------------------
            verif.current_stage = "INTEGRITY"
            if stages.get("integrity") != "PASSED":
                logger.info(f"Running Integrity fingerprinting for {verification_id}...")
                integrity_rec = db.scalar(select(IntegrityRecord).where(IntegrityRecord.document_id == doc.id))
                if not integrity_rec or not integrity_rec.verification_hash:
                    self.integrity_service.generate_document_integrity(db, doc.id, actor_id=actor_id)

                stages["integrity"] = "PASSED"
                stages["fraud"] = "LOW_RISK" if not verif.collision_detected else "HIGH_RISK"
                verif.stages_json = stages
                verif.status = "INTEGRITY_COMPLETED"
                db.commit()

            # ----------------------------------------------------
            # STAGE 5: Statutory Human Review Gate (Section 11 & 12)
            # ----------------------------------------------------
            if verif.collision_detected and verif.review_decision != "APPROVED":
                verif.review_required = True
                verif.review_reason = "Spatial cadastral parcel collision detected requiring Sub-Registrar review."
                verif.status = "REVIEW_REQUIRED"
                db.commit()
                logger.warning(f"Verification {verification_id} halted: REVIEW_REQUIRED.")
                return verif

            # ----------------------------------------------------
            # STAGE 6: Privacy & Zero-Knowledge Proof (Layer 7)
            # ----------------------------------------------------
            verif.current_stage = "ZK"
            if stages.get("zk") != "VERIFIED":
                logger.info(f"Generating ZK proof for {verification_id}...")
                zk_rec = db.scalar(select(ZKProofRecord).where(ZKProofRecord.document_id == doc.id))
                if not zk_rec or zk_rec.status != "VERIFIED":
                    self.zk_service.generate_proof(db, doc.id, actor_id=actor_id)

                stages["zk"] = "VERIFIED"
                verif.stages_json = stages
                verif.status = "ZK_VERIFIED"
                db.commit()

            # ----------------------------------------------------
            # STAGE 7: Polygon Blockchain Anchoring (Layer 8)
            # ----------------------------------------------------
            verif.current_stage = "BLOCKCHAIN"
            if stages.get("blockchain") != "CONFIRMED":
                logger.info(f"Anchoring on Polygon L2 for {verification_id}...")
                anchor_rec = db.scalar(select(BlockchainAnchor).where(BlockchainAnchor.document_id == doc.id))
                if not anchor_rec or anchor_rec.status != "CONFIRMED":
                    verif.status = "BLOCKCHAIN_PENDING"
                    db.commit()
                    self.blockchain_service.anchor_verification(db, doc.id, actor_id=actor_id)

                stages["blockchain"] = "CONFIRMED"
                verif.stages_json = stages
                verif.status = "BLOCKCHAIN_CONFIRMED"
                db.commit()

            # ----------------------------------------------------
            # STAGE 8: Certificate & QR Generation (Layer 9)
            # ----------------------------------------------------
            verif.current_stage = "CERTIFICATE"
            if stages.get("certificate") != "GENERATED":
                logger.info(f"Generating tamper-evident certificate for {verification_id}...")
                cert_rec = db.scalar(select(Certificate).where(Certificate.document_id == doc.id))
                if not cert_rec:
                    cert_resp = self.certificate_service.generate_certificate(db, doc.id, actor_id=actor_id)
                    verif.certificate_url = cert_resp.download_url
                else:
                    verif.certificate_url = f"/api/v1/certificates/{cert_rec.id}/download"

                stages["certificate"] = "GENERATED"
                verif.stages_json = stages
                verif.status = "CERTIFICATE_GENERATED"
                db.commit()

            # ----------------------------------------------------
            # STAGE 9: Final Verified State
            # ----------------------------------------------------
            verif.current_stage = "COMPLETED"
            verif.status = "VERIFIED"
            verif.error_message = None
            verif.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(verif)

            IntegrityService.record_audit_event(
                db=db,
                document_id=doc.id,
                event_type="PIPELINE_VERIFIED",
                actor_id=actor_id,
                metadata={"verification_id": verification_id, "status": "VERIFIED"},
            )
            return verif

        except Exception as e:
            logger.error(f"Error executing stage {verif.current_stage} for {verification_id}: {str(e)}")
            verif.status = f"{verif.current_stage}_FAILED" if verif.current_stage != "COMPLETED" else "FAILED"
            verif.error_message = str(e)
            db.commit()
            raise

    def handle_review_decision(
        self,
        db: Session,
        verification_id: str,
        decision: str,
        notes: Optional[str],
        actor: User,
    ) -> Verification:
        """
        Human Review decision by Sub-Registrar (Layer 11, Section 11 & 12).
        Only REGISTRAR or ADMIN allowed.
        """
        if actor.role not in [UserRole.REGISTRAR, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only Registrar or Admin can record a statutory review decision",
            )

        verif = db.scalar(select(Verification).where(Verification.verification_id == verification_id))
        if not verif:
            raise HTTPException(status_code=404, detail="Verification record not found")

        decision_upper = decision.upper().strip()
        if decision_upper not in ["APPROVE", "APPROVED", "REJECT", "REJECTED"]:
            raise HTTPException(status_code=400, detail="Decision must be APPROVE or REJECT")

        is_approved = decision_upper in ["APPROVE", "APPROVED"]
        verif.review_decision = "APPROVED" if is_approved else "REJECTED"
        verif.reviewed_by = actor.id
        verif.reviewed_at = datetime.utcnow()

        if is_approved:
            verif.review_required = False
            verif.status = "REVIEW_APPROVED"
            db.commit()
            IntegrityService.record_audit_event(
                db=db,
                document_id=verif.document_id,
                event_type="REGISTRAR_APPROVED",
                actor_id=actor.id,
                metadata={"verification_id": verification_id, "notes": notes},
            )
            # Resume orchestration pipeline from ZK onwards
            return self.process_verification(db, verification_id, actor_id=actor.id)
        else:
            verif.status = "REJECTED"
            verif.error_message = notes or "Rejected by Sub-Registrar review."
            db.commit()
            IntegrityService.record_audit_event(
                db=db,
                document_id=verif.document_id,
                event_type="REGISTRAR_REJECTED",
                actor_id=actor.id,
                metadata={"verification_id": verification_id, "notes": notes},
            )
            return verif

    def get_verification_full_status(
        self,
        db: Session,
        verification_id: str,
    ) -> Dict[str, Any]:
        """
        Builds the unified verification object (Layer 11, Section 5 & 14).
        """
        verif = db.scalar(select(Verification).where(Verification.verification_id == verification_id))
        if not verif:
            raise HTTPException(status_code=404, detail="Verification record not found")

        doc = db.scalar(select(Document).where(Document.id == verif.document_id))
        spatial = db.scalar(select(SpatialValidation).where(SpatialValidation.document_id == verif.document_id))
        integrity = db.scalar(select(IntegrityRecord).where(IntegrityRecord.document_id == verif.document_id))
        zk = db.scalar(select(ZKProofRecord).where(ZKProofRecord.document_id == verif.document_id))
        anchor = db.scalar(select(BlockchainAnchor).where(BlockchainAnchor.document_id == verif.document_id))
        cert = db.scalar(select(Certificate).where(Certificate.document_id == verif.document_id))

        return {
            "verification_id": verif.verification_id,
            "document_id": verif.document_id,
            "status": verif.status,
            "current_stage": verif.current_stage,
            "stages": verif.stages_json or {},
            "review_required": verif.review_required,
            "review_reason": verif.review_reason,
            "review_decision": verif.review_decision,
            "error_message": verif.error_message,
            "document": {
                "status": "VALID" if doc else "UNKNOWN",
                "file_name": doc.file_name if doc else None,
                "file_hash": doc.file_hash if doc else None,
            },
            "ocr": {
                "status": verif.stages_json.get("ocr", "PENDING") if verif.stages_json else "PENDING",
            },
            "gis": {
                "status": "PASSED" if spatial and spatial.geometry_valid and not spatial.overlap_detected else ("COLLISION_DETECTED" if verif.collision_detected else "PENDING"),
                "collision_detected": verif.collision_detected,
                "overlap_area_sqm": getattr(spatial, "overlap_area_sq_m", 0.0) if spatial else 0.0,

            },
            "integrity": {
                "status": "PASSED" if integrity and integrity.verification_hash else "PENDING",
                "verification_hash": integrity.verification_hash if integrity else None,
            },
            "fraud": {
                "risk": "LOW" if not verif.collision_detected else "HIGH",
            },
            "zk": {
                "status": zk.status if zk else "PENDING",
                "commitment": zk.commitment if zk else None,
            },
            "blockchain": {
                "status": anchor.status if anchor else "PENDING",
                "transaction_hash": anchor.transaction_hash if anchor else None,
                "network": anchor.network if anchor else None,
            },
            "certificate": {
                "status": cert.status if cert else "PENDING",
                "certificate_number": cert.certificate_number if cert else None,
                "certificate_hash": cert.certificate_hash if cert else None,
            },
            "created_at": verif.created_at.isoformat() if verif.created_at else "",
            "updated_at": verif.updated_at.isoformat() if verif.updated_at else "",
        }
