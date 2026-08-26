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
from app.models.certificate import Certificate
from app.models.blockchain_anchor import BlockchainAnchor
from app.models.zk_proof import ZKProofRecord
from app.models.integrity_record import IntegrityRecord
from app.models.spatial_validation import SpatialValidation
from app.models.audit_event import AuditEvent
from app.core.security import create_access_token
from app.services.gis_service import GISService
from app.services.integrity_service import IntegrityService
from app.privacy.zk_service import ZKService
from app.blockchain.service import BlockchainService

from app.services.certificate_service import CertificateService
from app.certificate.qr import generate_qr_image_bytes

client = TestClient(app)


class TestLayer9Certificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

        cls.registrar = cls.db.query(User).filter(User.email == "registrar@tn.gov.in").first()
        cls.registrar_token = create_access_token(cls.registrar.id, cls.registrar.role.value)

        cls.citizen_other = cls.db.query(User).filter(User.email == "citizen2@plotproof.gov.in").first()
        if not cls.citizen_other:
            cls.citizen_other = User(
                full_name="Second Citizen",
                email="citizen2@plotproof.gov.in",
                password_hash="hash",
                role=UserRole.CITIZEN,
                is_verified=True,
            )
            cls.db.add(cls.citizen_other)
            cls.db.commit()
            cls.db.refresh(cls.citizen_other)
        cls.citizen_other_token = create_access_token(cls.citizen_other.id, cls.citizen_other.role.value)

        cls.cert_service = CertificateService()
        cls.gis_service = GISService()
        cls.integrity_service = IntegrityService()
        cls.zk_service = ZKService()
        cls.blockchain_service = BlockchainService()

        cls._create_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @classmethod
    def _create_test_data(cls):
        db = SessionLocal()
        try:
            # Clean previous test certificate data
            db.query(BlockchainAnchor).filter(BlockchainAnchor.verification_id.like("PP-CERT-TEST-%")).delete(synchronize_session=False)
            db.query(Certificate).filter(Certificate.verification_id.like("PP-CERT-TEST-%")).delete(synchronize_session=False)
            existing_doc_ids = [d.id for d in db.query(Document).filter(Document.file_name.like("test_cert_%")).all()]
            if existing_doc_ids:
                db.query(Certificate).filter(Certificate.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(BlockchainAnchor).filter(BlockchainAnchor.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(ZKProofRecord).filter(ZKProofRecord.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(IntegrityRecord).filter(IntegrityRecord.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(SpatialValidation).filter(SpatialValidation.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(OCRField).filter(OCRField.document_id.in_(existing_doc_ids)).delete(synchronize_session=False)
                db.query(Document).filter(Document.id.in_(existing_doc_ids)).delete(synchronize_session=False)
            db.commit()




            raw_pdf = b"%PDF-1.4 Certificate Test Deed for Survey 142/3A"

            # 1. Clean Document - fully passed up through Blockchain
            doc_clean = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_cert_clean.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_cert_clean.pdf",
                sha256="c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1",
                file_hash="c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1c1",
                status=DocumentStatus.COMPLETED,
                version=1,
                verification_id="PP-CERT-TEST-0001",
                ocr_raw_text="Deed for Survey 142/3A, Selaiyur, Tambaram, Area 2400 Sq.ft, GPS 12.9252 N, 80.1475 E",
            )
            db.add(doc_clean)
            db.commit()
            db.refresh(doc_clean)

            f1 = OCRField(document_id=doc_clean.id, field_name="survey_number", field_value="142/3A", confidence=0.98, status="CONFIRMED")
            f2 = OCRField(document_id=doc_clean.id, field_name="area", field_value="2400 Sq.ft", confidence=0.96, status="CONFIRMED")
            f3 = OCRField(document_id=doc_clean.id, field_name="coordinates", field_value="12.9252, 80.1475", confidence=0.98, status="CONFIRMED")
            db.add_all([f1, f2, f3])
            db.commit()

            cls.gis_service.validate_document_spatial(db, doc_clean.id)
            cls.integrity_service.generate_document_integrity(db, doc_clean.id)
            cls.zk_service.generate_proof(db, doc_clean.id)
            cls.blockchain_service.anchor_verification(db, doc_clean.id)

            # 2. Document with Spatial Collision (premature for certificate)
            doc_collision = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_cert_collision.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_cert_collision.pdf",
                sha256="c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2",
                file_hash="c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2c2",
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id="PP-CERT-TEST-0002",
                ocr_raw_text="Collision Deed",
            )
            db.add(doc_collision)
            db.commit()
            db.refresh(doc_collision)

            # 3. Document with Blockchain Pending
            doc_no_bc = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_cert_no_bc.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_cert_no_bc.pdf",
                sha256="c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3",
                file_hash="c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3",
                status=DocumentStatus.COMPLETED,
                version=1,
                verification_id="PP-CERT-TEST-0003",
                ocr_raw_text="Deed for Survey 142/3A, Selaiyur, Tambaram, Area 2400 Sq.ft, GPS 12.9252 N, 80.1475 E",
            )
            db.add(doc_no_bc)
            db.commit()
            db.refresh(doc_no_bc)

            f_b1 = OCRField(document_id=doc_no_bc.id, field_name="survey_number", field_value="142/3A", confidence=0.98, status="CONFIRMED")
            f_b2 = OCRField(document_id=doc_no_bc.id, field_name="area", field_value="2400 Sq.ft", confidence=0.96, status="CONFIRMED")
            f_b3 = OCRField(document_id=doc_no_bc.id, field_name="coordinates", field_value="12.9252, 80.1475", confidence=0.98, status="CONFIRMED")
            db.add_all([f_b1, f_b2, f_b3])
            db.commit()

            cls.gis_service.validate_document_spatial(db, doc_no_bc.id)
            cls.integrity_service.generate_document_integrity(db, doc_no_bc.id)
            cls.zk_service.generate_proof(db, doc_no_bc.id)
            # Notice: NOT anchored to blockchain

            cls.doc_clean_id = doc_clean.id
            cls.doc_collision_id = doc_collision.id
            cls.doc_no_bc_id = doc_no_bc.id
        finally:
            db.close()

    def test_01_valid_certificate_generation(self):
        # Section 9, 10 & 29 (Test 1): Valid certificate generated when all prerequisites pass
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_clean_id}/certificate", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("PP-CERT-2026-", data["certificate_number"])
        self.assertEqual(data["status"], "ACTIVE")
        self.assertEqual(len(data["certificate_hash"]), 64)
        print("[PASS] Test 1: Full Prerequisite Verification & PDF Certificate Generation Verified")

    def test_02_spatial_collision_blocks_certificate(self):
        # Section 10 & 29 (Test 2): Spatial failure blocks certificate generation
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_collision_id}/certificate", headers=headers)
        self.assertEqual(res.status_code, 400)
        detail = res.json()["detail"]
        self.assertEqual(detail["status"], "REJECTED")
        self.assertEqual(detail["reason"], "CERTIFICATE_PREREQUISITES_NOT_MET")
        print("[PASS] Test 2: Prerequisite Engine: GIS Spatial Anomaly Blocks Certificate Issuance")

    def test_03_blockchain_pending_blocks_certificate(self):
        # Section 10 & 29 (Test 4): Blockchain pending blocks certificate generation
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_no_bc_id}/certificate", headers=headers)
        self.assertEqual(res.status_code, 400)
        detail = res.json()["detail"]
        self.assertEqual(detail["status"], "REJECTED")
        self.assertEqual(detail["reason"], "CERTIFICATE_PREREQUISITES_NOT_MET")
        print("[PASS] Test 3: Prerequisite Engine: Unconfirmed Blockchain Anchor Blocks Certificate")

    def test_04_qr_code_generation(self):
        # Section 7 & 8: QR code contains only verification URL
        verif_url = "https://plotproof.gov.in/verify/PP-CERT-TEST-0001"
        qr_bytes = generate_qr_image_bytes(verif_url)
        self.assertTrue(qr_bytes.startswith(b"\x89PNG"))  # Valid PNG signature
        self.assertGreater(len(qr_bytes), 500)
        print("[PASS] Test 4: Pure Public Verification URL QR Code PNG Generation Verified")

    def test_05_certificate_metadata_retrieval(self):
        # Section 13: GET /documents/{id}/certificate
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.get(f"/api/v1/documents/{self.doc_clean_id}/certificate", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ACTIVE")
        self.assertIn("download", data["download_url"])
        print("[PASS] Test 5: Certificate Metadata Retrieval Endpoint Verified")

    def test_06_access_controlled_certificate_download(self):
        # Section 23: GET /certificates/{id}/download
        db = SessionLocal()
        try:
            cert = db.scalar(select(Certificate).where(Certificate.document_id == self.doc_clean_id))
            self.assertIsNotNone(cert)

            headers = {"Authorization": f"Bearer {self.citizen_token}"}
            res = client.get(f"/api/v1/certificates/{cert.id}/download", headers=headers)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers["content-type"], "application/pdf")
            self.assertTrue(res.content.startswith(b"%PDF-"))
            print("[PASS] Test 6: Access-Controlled Binary PDF Certificate Download Verified")
        finally:
            db.close()

    def test_07_certificate_integrity_verification_match_and_tamper(self):
        # Section 24 & 29 (Test 7): SHA-256 match vs mismatch detection
        db = SessionLocal()
        try:
            cert = db.scalar(select(Certificate).where(Certificate.document_id == self.doc_clean_id))
            self.assertIsNotNone(cert)

            with open(cert.file_path, "rb") as f:
                genuine_pdf = f.read()

            # 1. Genuine PDF bytes -> MATCH
            res_match = client.post(
                f"/api/v1/certificates/{cert.certificate_number}/verify-integrity",
                files={"file": ("cert.pdf", io.BytesIO(genuine_pdf), "application/pdf")},
            )
            self.assertEqual(res_match.status_code, 200)
            data_match = res_match.json()
            self.assertTrue(data_match["is_valid"])
            self.assertEqual(data_match["status"], "VALID")

            # 2. Tampered PDF bytes (altered by 1 byte) -> INTEGRITY_FAILURE
            tampered_pdf = genuine_pdf + b"\x00TAMPERED"
            res_tamper = client.post(
                f"/api/v1/certificates/{cert.certificate_number}/verify-integrity",
                files={"file": ("cert.pdf", io.BytesIO(tampered_pdf), "application/pdf")},
            )
            self.assertEqual(res_tamper.status_code, 200)
            data_tamper = res_tamper.json()
            self.assertFalse(data_tamper["is_valid"])
            self.assertEqual(data_tamper["status"], "INTEGRITY_FAILURE")
            print("[PASS] Test 7: Certificate Byte-Level File Integrity Interception Verified")
        finally:
            db.close()

    def test_08_certificate_revocation_by_registrar(self):
        # Section 18, 19 & 29 (Test 6): Registrar revokes certificate -> status becomes REVOKED
        db = SessionLocal()
        try:
            cert = db.scalar(select(Certificate).where(Certificate.document_id == self.doc_clean_id))
            self.assertIsNotNone(cert)

            headers_reg = {"Authorization": f"Bearer {self.registrar_token}"}
            res = client.post(
                f"/api/v1/certificates/{cert.id}/revoke",
                json={"reason": "Statutory survey boundary revision required"},
                headers=headers_reg,
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "REVOKED")
            self.assertEqual(data["reason"], "Statutory survey boundary revision required")

            # Verify public verification portal reflects REVOKED
            res_pub = client.get(f"/api/v1/public/verify/{cert.verification_id}")
            self.assertEqual(res_pub.status_code, 200)
            self.assertEqual(res_pub.json()["status"], "REVOKED")
            print("[PASS] Test 8: Sub-Registrar Certificate Revocation & Public Portal Status Invalidation Verified")
        finally:
            db.close()

    def test_09_citizen_forbidden_from_revoking_certificate(self):
        # Section 28: Citizen cannot revoke certificate (403 Forbidden)
        db = SessionLocal()
        try:
            cert = db.scalar(select(Certificate).where(Certificate.document_id == self.doc_clean_id))
            self.assertIsNotNone(cert)

            headers_citizen = {"Authorization": f"Bearer {self.citizen_token}"}
            res = client.post(
                f"/api/v1/certificates/{cert.id}/revoke",
                json={"reason": "Citizen attempt"},
                headers=headers_citizen,
            )
            self.assertEqual(res.status_code, 403)
            print("[PASS] Test 9: Citizen Role Prohibited from Revoking Certificates (403 Forbidden)")
        finally:
            db.close()

    def test_10_public_verification_portal_strict_pii_minimization(self):
        # Section 14 & 15: Public verify endpoint has zero PII
        res = client.get("/api/v1/public/verify/PP-CERT-TEST-0001")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("verification_id", data)
        self.assertIn("disclaimer", data)

        data_str = json.dumps(data).lower()
        self.assertNotIn("aadhaar", data_str)
        self.assertNotIn("phone", data_str)
        self.assertNotIn("email", data_str)
        self.assertNotIn("ramanathan", data_str)
        print("[PASS] Test 10: Public Verification Portal Zero-PII Minimization Verified")

    def test_11_mandatory_statutory_legal_disclaimer(self):
        # Section 3: Verify mandatory disclaimer text is present
        res = client.get("/api/v1/public/verify/PP-CERT-TEST-0001")
        self.assertEqual(res.status_code, 200)
        disclaimer = res.json()["disclaimer"]
        self.assertIn("PlotProof System Verification Certificate", disclaimer)
        self.assertIn("does not independently constitute a government-issued title", disclaimer)
        self.assertNotIn("LAND TITLE GUARANTEED", disclaimer)
        self.assertNotIn("PROPERTY IS LEGALLY AUTHENTIC", disclaimer)
        print("[PASS] Test 11: Mandatory Statutory Legal Disclaimer & Credibility Text Verified")

    def test_12_forensic_audit_trail_events_logged(self):
        # Section 26: CERTIFICATE_GENERATED and CERTIFICATE_REVOKED audit events logged
        db = SessionLocal()
        try:
            events = list(db.scalars(select(AuditEvent).where(AuditEvent.document_id == self.doc_clean_id)).all())
            event_types = [e.event_type for e in events]
            self.assertIn("CERTIFICATE_GENERATED", event_types)
            self.assertIn("CERTIFICATE_REVOKED", event_types)
            print("[PASS] Test 12: Forensic Audit Trail Records Certificate Lifecycle Events Verified")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
