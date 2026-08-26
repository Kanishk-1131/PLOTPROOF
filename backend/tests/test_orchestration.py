import io
import json
import sys
import unittest
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus
from app.models.ocr_field import OCRField
from app.models.verification import Verification
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.certificate import Certificate
from app.models.audit_event import AuditEvent
from app.core.security import create_access_token
from app.services.orchestrator import OrchestratorService

client = TestClient(app)


class TestLayer11Orchestration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

        cls.registrar = cls.db.query(User).filter(User.email == "registrar@tn.gov.in").first()
        cls.registrar_token = create_access_token(cls.registrar.id, cls.registrar.role.value)

        cls.orchestrator = OrchestratorService()
        cls._create_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @classmethod
    def _create_test_data(cls):
        db = SessionLocal()
        try:
            # Clean previous test records
            db.query(Verification).filter(Verification.verification_id.like("PP-ORCH-TEST-%")).delete(synchronize_session=False)
            db.query(Certificate).filter(Certificate.verification_id.like("PP-ORCH-TEST-%")).delete(synchronize_session=False)
            db.query(BlockchainAnchor).filter(BlockchainAnchor.verification_id.like("PP-ORCH-TEST-%")).delete(synchronize_session=False)
            existing_doc_ids = [d.id for d in db.query(Document).filter(Document.file_name.like("test_orch_%")).all()]
            if existing_doc_ids:
                db.query(OCRField).filter(OCRField.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(Document).filter(Document.id.in_(existing_doc_ids)).delete(synchronize_session=False)
            db.commit()

            raw_pdf = b"%PDF-1.4 Orchestration Clean Deed for Survey 142/3A"

            # 1. Clean Document
            doc_clean = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_orch_clean.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_orch_clean.pdf",
                sha256="e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1",
                file_hash="e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1e1",
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id="PP-ORCH-TEST-0001",
                ocr_raw_text="Deed for Survey 142/3A, Selaiyur, Tambaram, Area 2400 Sq.ft, GPS 12.9252 N, 80.1475 E",
            )
            db.add(doc_clean)
            db.commit()
            db.refresh(doc_clean)

            f1 = OCRField(document_id=doc_clean.id, field_name="survey_number", field_value="142/3A", confidence=0.98, status="CONFIRMED")
            f2 = OCRField(document_id=doc_clean.id, field_name="area", field_value="2400 Sq.ft", confidence=0.96, status="CONFIRMED")
            f3 = OCRField(document_id=doc_clean.id, field_name="coordinates", field_value="12.9252, 80.1475", confidence=0.98, status="CONFIRMED")
            db.add_all([f1, f2, f3])

            # 2. Collision Document (for manual review)
            doc_collision = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_orch_collision.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_orch_collision.pdf",
                sha256="e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2",
                file_hash="e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2e2",
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id="PP-ORCH-TEST-0002",
                ocr_raw_text="Collision Deed Survey 142/3A Overlap",
            )
            db.add(doc_collision)

            # 3. Collision Document for Rejection
            doc_reject = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_orch_collision_reject.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_orch_collision_reject.pdf",
                sha256="e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3",
                file_hash="e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3e3",
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id="PP-ORCH-TEST-0003",
                ocr_raw_text="Collision Deed to be rejected",
            )
            db.add(doc_reject)
            db.commit()

            cls.doc_clean_id = doc_clean.id
            cls.doc_collision_id = doc_collision.id
            cls.doc_reject_id = doc_reject.id
        finally:
            db.close()

    def test_01_full_orchestration_pipeline_success(self):
        # Section 4 & 7: Start verification runs entire pipeline to VERIFIED
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(
            "/api/v1/verifications",
            json={"document_id": self.doc_clean_id},
            headers=headers,
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["status"], "VERIFIED")
        self.assertEqual(data["current_stage"], "COMPLETED")
        self.assertEqual(data["stages"]["document"], "COMPLETED")
        self.assertEqual(data["stages"]["ocr"], "COMPLETED")
        self.assertEqual(data["stages"]["gis"], "PASSED")
        self.assertEqual(data["stages"]["integrity"], "PASSED")
        self.assertEqual(data["stages"]["zk"], "VERIFIED")
        self.assertEqual(data["stages"]["blockchain"], "CONFIRMED")
        self.assertEqual(data["stages"]["certificate"], "GENERATED")
        print("[PASS] Test 1: Full End-to-End Orchestration Pipeline Execution Verified (UPLOADED -> VERIFIED)")

    def test_02_central_state_machine_stages_progression(self):
        # Section 1: Verify all stages are completed in stages dictionary
        res = client.get("/api/v1/verifications/PP-ORCH-TEST-0001")
        self.assertEqual(res.status_code, 200)
        stages = res.json()["stages"]
        self.assertEqual(stages["ocr"], "COMPLETED")
        self.assertEqual(stages["gis"], "PASSED")
        self.assertEqual(stages["integrity"], "PASSED")
        self.assertEqual(stages["zk"], "VERIFIED")
        self.assertEqual(stages["blockchain"], "CONFIRMED")
        self.assertEqual(stages["certificate"], "GENERATED")
        print("[PASS] Test 2: Central State Machine Multi-Stage Progression Formally Verified")

    def test_03_spatial_collision_halts_at_review_required(self):
        # Section 11: Collision halts pipeline at REVIEW_REQUIRED, no ZK, no Blockchain, no Cert
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(
            "/api/v1/verifications",
            json={"document_id": self.doc_collision_id},
            headers=headers,
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["status"], "REVIEW_REQUIRED")
        self.assertTrue(data["review_required"])
        self.assertEqual(data["stages"]["gis"], "COLLISION_DETECTED")
        self.assertEqual(data["stages"]["zk"], "PENDING")
        self.assertEqual(data["stages"]["blockchain"], "PENDING")
        self.assertEqual(data["stages"]["certificate"], "PENDING")
        print("[PASS] Test 3: Spatial Collision Intercepted & Pipeline Halted at REVIEW_REQUIRED (No ZK/Blockchain/Cert)")

    def test_04_sub_registrar_approval_resumes_orchestration(self):
        # Section 11 & 12: Sub-Registrar approves -> pipeline resumes and completes to VERIFIED
        headers = {"Authorization": f"Bearer {self.registrar_token}"}
        res = client.post(
            "/api/v1/verifications/PP-ORCH-TEST-0002/review",
            json={"decision": "APPROVE", "notes": "Approved following boundary survey verification."},
            headers=headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "VERIFIED")
        self.assertEqual(data["review_decision"], "APPROVED")
        self.assertFalse(data["review_required"])
        self.assertEqual(data["stages"]["zk"], "VERIFIED")
        self.assertEqual(data["stages"]["blockchain"], "CONFIRMED")
        self.assertEqual(data["stages"]["certificate"], "GENERATED")
        print("[PASS] Test 4: Sub-Registrar Review Approval Resumes Pipeline to VERIFIED")

    def test_05_sub_registrar_rejection_halts_orchestration(self):
        # Section 12: Sub-Registrar rejects -> pipeline sets REJECTED and terminates
        headers_start = {"Authorization": f"Bearer {self.citizen_token}"}
        client.post("/api/v1/verifications", json={"document_id": self.doc_reject_id}, headers=headers_start)

        headers_reg = {"Authorization": f"Bearer {self.registrar_token}"}
        res = client.post(
            "/api/v1/verifications/PP-ORCH-TEST-0003/review",
            json={"decision": "REJECT", "notes": "Overlapping boundary cannot be reconciled."},
            headers=headers_reg,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "REJECTED")
        self.assertEqual(data["review_decision"], "REJECTED")
        self.assertEqual(data["stages"]["zk"], "PENDING")
        self.assertEqual(data["stages"]["blockchain"], "PENDING")
        print("[PASS] Test 5: Sub-Registrar Review Rejection Terminates Pipeline without Anchoring")

    def test_06_unauthorized_citizen_review_intercepted(self):
        # Section 11: Citizen role cannot approve or reject review
        headers_citizen = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(
            "/api/v1/verifications/PP-ORCH-TEST-0003/review",
            json={"decision": "APPROVE", "notes": "Unauthorized citizen approval attempt"},
            headers=headers_citizen,
        )
        self.assertEqual(res.status_code, 403)
        print("[PASS] Test 6: Citizen Role Prohibited from Overriding Statutory Review (403 Forbidden)")

    def test_07_idempotency_avoids_duplicate_recomputations(self):
        # Section 9: Re-triggering verification does not duplicate blockchain anchors or certs
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res1 = client.post("/api/v1/verifications", json={"document_id": self.doc_clean_id}, headers=headers)
        self.assertEqual(res1.status_code, 201)

        db = SessionLocal()
        try:
            anchor_count = db.query(BlockchainAnchor).filter(BlockchainAnchor.document_id == self.doc_clean_id).count()
            cert_count = db.query(Certificate).filter(Certificate.document_id == self.doc_clean_id).count()
            self.assertEqual(anchor_count, 1)
            self.assertEqual(cert_count, 1)
            print("[PASS] Test 7: Idempotent Execution Prevents Duplicate Anchors and Certificates")
        finally:
            db.close()

    def test_08_never_lose_progress_resume_support(self):
        # Section 8 & 10: Retry endpoint resumes verification from current stage
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post("/api/v1/verifications/PP-ORCH-TEST-0001/retry", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "VERIFIED")
        print("[PASS] Test 8: Failure Recovery & Never-Lose-Progress Resume Endpoint Verified")

    def test_09_forensic_audit_trail_captures_all_orchestration_events(self):
        # Section 13: Audit events recorded for transitions
        db = SessionLocal()
        try:
            events = list(db.scalars(select(AuditEvent).where(AuditEvent.document_id == self.doc_clean_id)).all())
            types = [e.event_type for e in events]
            self.assertIn("ORCHESTRATION_STARTED", types)
            self.assertIn("PIPELINE_VERIFIED", types)
            print("[PASS] Test 9: Forensic Audit Trail Records End-to-End Orchestration Transitions")
        finally:
            db.close()

    def test_10_full_verification_object_contract_compliance(self):
        # Section 14: Verification object contains all required sub-objects
        res = client.get("/api/v1/verifications/PP-ORCH-TEST-0001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("document", data)
        self.assertIn("ocr", data)
        self.assertIn("gis", data)
        self.assertIn("integrity", data)
        self.assertIn("fraud", data)
        self.assertIn("zk", data)
        self.assertIn("blockchain", data)
        self.assertIn("certificate", data)
        self.assertEqual(data["blockchain"]["status"], "CONFIRMED")
        self.assertEqual(data["certificate"]["status"], "ACTIVE")
        print("[PASS] Test 10: Full Layer 11 Integrated Response Contract Compliance Verified")

    def test_11_live_tracking_endpoint_accuracy(self):
        # Section 5: Real-time progress endpoint
        res = client.get("/api/v1/verifications/PP-ORCH-TEST-0001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["verification_id"], "PP-ORCH-TEST-0001")
        self.assertEqual(data["status"], "VERIFIED")
        print("[PASS] Test 11: Real-Time Live Progression Tracking Query Verified")

    def test_12_public_verification_portal_reflects_orchestrated_state(self):
        # Section 16: Public portal matches orchestrated verification state
        res = client.get("/api/v1/public/verify/PP-ORCH-TEST-0001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "VERIFIED")
        self.assertEqual(data["blockchain_anchor"], "CONFIRMED")
        print("[PASS] Test 12: Public QR Verification Portal Synchronized with Orchestrated State Verified")


if __name__ == "__main__":
    unittest.main()
