import io
import sys
import unittest
import uuid
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus
from app.models.ocr_field import OCRField
from app.models.verification import Verification
from app.models.certificate import Certificate
from app.models.blockchain_anchor import BlockchainAnchor
from app.core.security import create_access_token
from app.services.orchestrator import OrchestratorService
from app.services.certificate_service import CertificateService

client = TestClient(app)


class TestIntegrationCertificatePipeline(unittest.TestCase):
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
        cls.cert_service = CertificateService()
        cls._setup_clean_document()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @classmethod
    def _setup_clean_document(cls):
        db = SessionLocal()
        try:
            vid = "PP-CERT-PIPE-0001"
            db.query(Verification).filter(Verification.verification_id == vid).delete(synchronize_session=False)
            db.query(Certificate).filter(Certificate.verification_id == vid).delete(synchronize_session=False)
            db.query(BlockchainAnchor).filter(BlockchainAnchor.verification_id == vid).delete(synchronize_session=False)
            from app.models.spatial_validation import SpatialValidation
            from app.models.integrity_record import IntegrityRecord
            old_doc = db.query(Document).filter(Document.verification_id == vid).first()
            if old_doc:
                db.query(SpatialValidation).filter(SpatialValidation.document_id == old_doc.id).delete(synchronize_session=False)
                db.query(IntegrityRecord).filter(IntegrityRecord.document_id == old_doc.id).delete(synchronize_session=False)
                db.query(OCRField).filter(OCRField.document_id == old_doc.id).delete(synchronize_session=False)
                db.delete(old_doc)
            db.commit()


            doc = Document(
                owner_user_id=cls.citizen.id,
                file_name="cert_pipe_clean.pdf",
                mime_type="application/pdf",
                file_size=2000,
                storage_key="test/cert_pipe_clean.pdf",
                sha256="c" * 64,
                file_hash="c" * 64,
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id=vid,
                ocr_raw_text="Clean deed Survey 142/3A, Selaiyur, Tambaram, Area 2400 Sq.ft, GPS 12.9252 N, 80.1475 E",
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            f1 = OCRField(document_id=doc.id, field_name="survey_number", field_value="142/3A", confidence=0.98, status="CONFIRMED")
            f2 = OCRField(document_id=doc.id, field_name="area", field_value="2400 Sq.ft", confidence=0.96, status="CONFIRMED")
            f3 = OCRField(document_id=doc.id, field_name="coordinates", field_value="12.9252, 80.1475", confidence=0.98, status="CONFIRMED")
            db.add_all([f1, f2, f3])
            db.commit()
            cls.test_doc_id = doc.id
            cls.test_vid = vid
        finally:
            db.close()

    def test_01_full_certificate_issuance_and_byte_integrity(self):
        db = SessionLocal()
        try:
            # 1. Run orchestration to completion
            self.orchestrator.start_verification(db, self.test_doc_id)

            # 2. Generate Certificate
            cert_resp = self.cert_service.generate_certificate(db, self.test_doc_id)
            self.assertEqual(cert_resp.status, "ACTIVE")
            self.assertTrue(cert_resp.certificate_number.startswith("PP-CERT-"))

            # 3. Verify byte integrity check via REST API
            cert = db.query(Certificate).filter(Certificate.document_id == self.test_doc_id).first()
            with open(cert.file_path, "rb") as f:
                pdf_bytes = f.read()


            files = {"file": ("cert.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
            res = client.post(f"/api/v1/certificates/{cert_resp.certificate_number}/verify-integrity", files=files)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.json()["status"], "VALID")
            self.assertTrue(res.json()["is_valid"])
            print("[PASS] Integration Test 1: Full Certificate Generation & Byte-Level SHA-256 Tamper Verification")

        finally:
            db.close()

    def test_02_certificate_revocation_and_public_portal(self):
        db = SessionLocal()
        try:
            cert = db.query(Certificate).filter(Certificate.document_id == self.test_doc_id).first()
            self.assertIsNotNone(cert)

            # Revoke as Sub-Registrar
            headers = {"Authorization": f"Bearer {self.registrar_token}"}
            res_revoke = client.post(
                f"/api/v1/certificates/{cert.id}/revoke",
                json={"reason": "Court stay order pending boundary survey"},
                headers=headers,
            )
            self.assertEqual(res_revoke.status_code, 200)
            self.assertEqual(res_revoke.json()["status"], "REVOKED")

            # Check public verification portal reflects REVOKED status
            res_pub = client.get(f"/api/v1/public/verify/{self.test_vid}")
            self.assertEqual(res_pub.status_code, 200)
            self.assertEqual(res_pub.json()["status"], "REVOKED")
            print("[PASS] Integration Test 2: Sub-Registrar Certificate Revocation & Public Portal Invalidation")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
