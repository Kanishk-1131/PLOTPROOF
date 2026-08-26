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
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.ocr_field import OCRField
from app.models.zk_proof import ZKProofRecord
from app.core.security import create_access_token
from app.privacy.commitments import (
    compute_poseidon_commitment,
    generate_commitment_secret,
    create_deed_commitment,
    BN254_PRIME,
)
from app.privacy.privacy_policy import sanitize_for_public_presentation
from app.privacy.zk_service import ZKService
from app.services.gis_service import GISService
from app.services.integrity_service import IntegrityService

client = TestClient(app)


class TestLayer7Privacy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

        cls.registrar = cls.db.query(User).filter(User.email == "registrar@tn.gov.in").first()
        cls.registrar_token = create_access_token(cls.registrar.id, cls.registrar.role.value)

        # Second citizen for unauthorized tenancy isolation (Section 27 Test 5)
        from app.models.user import UserRole
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

        cls.other_user = cls.db.query(User).filter(User.email == "auditor@hdfcbank.com").first()
        cls.other_token = create_access_token(cls.other_user.id, cls.other_user.role.value)


        cls.zk_service = ZKService()
        cls.gis_service = GISService()
        cls.integrity_service = IntegrityService()

        cls._create_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @classmethod
    def _create_test_data(cls):
        db = SessionLocal()
        try:
            # Clean previous test privacy docs
            db.query(Document).filter(Document.file_name.like("test_privacy_%")).delete(synchronize_session=False)
            db.commit()

            # 1. Clean Title Document (Approved)
            raw_pdf = b"%PDF-1.4 Privacy test deed for Survey 142/3A"
            doc_clean = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_privacy_clean.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_privacy_clean.pdf",
                sha256="7777777777777777777777777777777777777777777777777777777777777777",
                file_hash="7777777777777777777777777777777777777777777777777777777777777777",
                status=DocumentStatus.COMPLETED,
                version=1,
                verification_id="PP-ZK-2026-0001",
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

            # Run GIS and Integrity
            cls.gis_service.validate_document_spatial(db, doc_clean.id)
            cls.integrity_service.generate_document_integrity(db, doc_clean.id)

            # 2. Unapproved Document with Spatial Collision (fails prerequisites)
            doc_failing = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_privacy_collision_doc.pdf",
                mime_type="application/pdf",
                file_size=len(raw_pdf),
                storage_key="test/test_privacy_collision_doc.pdf",
                sha256="8888888888888888888888888888888888888888888888888888888888888888",
                file_hash="8888888888888888888888888888888888888888888888888888888888888888",
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id="PP-ZK-2026-0002",
                ocr_raw_text="Collision deed on 142/3B",
            )
            db.add(doc_failing)
            db.commit()
            db.refresh(doc_failing)

            cls.doc_clean_id = doc_clean.id
            cls.doc_failing_id = doc_failing.id
        finally:
            db.close()

    def test_01_poseidon_commitment_determinism(self):
        # Section 4 & 5: Poseidon commitment is deterministic and bounded in BN254 scalar field
        p_record = "12345678901234567890"
        secret = "98765432109876543210"
        c1 = compute_poseidon_commitment(p_record, secret)
        c2 = compute_poseidon_commitment(p_record, secret)

        self.assertEqual(c1, c2)
        self.assertLess(int(c1), BN254_PRIME)
        print("[PASS] Test 1: Poseidon Algebraic Commitment Determinism & Field Bounding Verified")

    def test_02_wrong_secret_changes_commitment(self):
        # Section 27: Test 2 - Correct private input + Wrong secret -> Different commitment
        p_record = "12345678901234567890"
        secret_correct = "98765432109876543210"
        secret_wrong = "98765432109876543211"

        c_correct = compute_poseidon_commitment(p_record, secret_correct)
        c_wrong = compute_poseidon_commitment(p_record, secret_wrong)

        self.assertNotEqual(c_correct, c_wrong)
        print("[PASS] Test 2: Commitment Non-Collision with Altered Secret Verified")

    def test_03_wrong_commitment_verification_failure(self):
        # Section 27: Test 3 - Proof verification fails if public commitment signal is tampered
        proof = {
            "pi_a": ["0x1", "0x2", "1"],
            "pi_b": [["0x3", "0x4"], ["0x5", "0x6"], ["1", "0"]],
            "pi_c": ["0x7", "0x8", "1"],
            "protocol": "groth16",
        }
        # Incomplete/tampered signals: validationStatus is 0 instead of 1
        tampered_signals = ["123456789", "0"]
        is_valid = self.zk_service._verify_groth16_proof_data(proof, tampered_signals)
        self.assertFalse(is_valid)
        print("[PASS] Test 3: Constraint Enforcement Rejects Proof with Invalid Signals")

    def test_04_modified_verification_state_invalidates_commitment(self):
        # Section 27: Test 4 - If verification state changes, commitment changes
        p_rec_v1, comm_v1 = create_deed_commitment("doc_hash_1", "verif_hash_v1", "secret_1")
        p_rec_v2, comm_v2 = create_deed_commitment("doc_hash_1", "verif_hash_v2", "secret_1")

        self.assertNotEqual(comm_v1, comm_v2)
        print("[PASS] Test 4: Verification Hash Modification Automatically Invalidates Commitment")

    def test_05_unauthorized_proof_request_forbidden(self):
        # Section 27: Test 5 - User A cannot generate proof for User B document (403 Forbidden)
        headers_other = {"Authorization": f"Bearer {self.citizen_other_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_clean_id}/privacy/prove", headers=headers_other)
        self.assertEqual(res.status_code, 403)

        print("[PASS] Test 5: Cross-Tenant Proof Generation Request Strictly Intercepted (403 Forbidden)")

    def test_06_commitment_creation_endpoint(self):
        # Section 17: POST /documents/{id}/privacy/commit returns commitment without leaking secrets
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_clean_id}/privacy/commit", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["document_id"], self.doc_clean_id)
        self.assertIn("COM-", data["commitment_id"])
        self.assertEqual(data["status"], "CREATED")
        # Ensure no private fields leaked
        self.assertNotIn("secret", data)
        self.assertNotIn("privateRecord", data)
        print("[PASS] Test 6: Commitment Endpoint Generates Public ID and Conceals Secret")

    def test_07_prerequisite_validation_enforcement(self):
        # Section 18: Rejects prove if document has not passed verification
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_failing_id}/privacy/prove", headers=headers)
        self.assertEqual(res.status_code, 400)
        detail = res.json()["detail"]
        self.assertEqual(detail["status"], "REJECTED")
        self.assertEqual(detail["reason"], "VERIFICATION_PREREQUISITES_NOT_MET")
        print("[PASS] Test 7: Prerequisite Engine Prohibits ZK Proof for Unapproved/Colliding Deed")

    def test_08_proof_generation_and_local_verification(self):
        # Section 21 & 22: Generates proof and locally verifies before storing
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(f"/api/v1/documents/{self.doc_clean_id}/privacy/prove", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["document_id"], self.doc_clean_id)
        self.assertIn("ZKP-", data["proof_id"])
        self.assertEqual(data["status"], "VALID")
        self.assertEqual(data["circuit_version"], "land-verification-v1")
        self.assertEqual(data["verification_key_version"], "vk-v1")
        self.assertEqual(data["public_signals"][1], "1")
        print("[PASS] Test 8: Groth16 Proof Generation with Local Verification Gate Verified")

    def test_09_proof_verification_endpoint(self):
        # Section 15 & 16: POST /privacy/verify checks existing proof record
        db = SessionLocal()
        try:
            zk_rec = db.scalar(select(ZKProofRecord).where(ZKProofRecord.document_id == self.doc_clean_id))
            self.assertIsNotNone(zk_rec)

            headers = {"Authorization": f"Bearer {self.citizen_token}"}
            res = client.post(
                f"/api/v1/documents/{self.doc_clean_id}/privacy/verify?proof_id={zk_rec.proof_id}",
                headers=headers,
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["is_valid"])
            self.assertEqual(data["status"], "VERIFIED")
            print("[PASS] Test 9: Proof Verification REST Endpoint Successfully Evaluated")
        finally:
            db.close()

    def test_10_privacy_policy_pii_sanitization(self):
        # Section 10 & 24: Verifies PII is scrubbed from public objects
        sensitive_payload = {
            "verification_id": "PP-2026-000052",
            "owner_name": "K. S. Ramanathan",
            "aadhaar_uid": "5412-8823-8912",
            "phone": "+91 98401 23456",
            "secret": "999888777666",
            "witness": {"private_record": 123},
            "commitment": "0x12345678",
        }
        clean = sanitize_for_public_presentation(sensitive_payload)
        self.assertIn("verification_id", clean)
        self.assertIn("commitment", clean)
        self.assertNotIn("owner_name", clean)
        self.assertNotIn("aadhaar_uid", clean)
        self.assertNotIn("phone", clean)
        self.assertNotIn("secret", clean)
        self.assertNotIn("witness", clean)
        print("[PASS] Test 10: Strict Privacy Policy Sanitization Scrubbing All Citizen PII Verified")

    def test_11_privacy_status_endpoint(self):
        # Section 24: GET /privacy/status shows protected summary
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.get(f"/api/v1/documents/{self.doc_clean_id}/privacy/status", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["private_identity"], "PROTECTED")
        self.assertEqual(data["sensitive_data_exposed"], "NO")
        self.assertEqual(data["zk_proof"], "VERIFIED")
        print("[PASS] Test 11: Privacy Status Dashboard Payload Compliance Verified")

    def test_12_layer_8_blockchain_handshake_payload(self):
        # Section 25: Standardized handshake payload for Layer 8
        db = SessionLocal()
        try:
            handshake = self.zk_service.build_blockchain_handshake(db, self.doc_clean_id)
            self.assertEqual(handshake.verification_id, "PP-ZK-2026-0001")
            self.assertEqual(handshake.status, "ZK_VERIFIED")
            self.assertIn("0x", handshake.zk_proof["pi_a"][0])
            self.assertEqual(handshake.circuit_version, "land-verification-v1")
            print("[PASS] Test 12: Standardized Layer 7 -> Layer 8 Blockchain Handshake Payload Verified")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
