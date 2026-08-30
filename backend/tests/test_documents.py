import io
import sys
import unittest
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User, UserRole
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.models.audit_log import AuditLog
from app.core.security import hash_password, create_access_token

client = TestClient(app)


class TestLayer3DocumentIngestion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        # Seed or fetch citizen 1
        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

        # Seed or fetch registrar
        cls.registrar = cls.db.query(User).filter(User.email == "registrar@tn.gov.in").first()
        cls.registrar_token = create_access_token(cls.registrar.id, cls.registrar.role.value)

        # Create second citizen to test ownership boundary
        cls.other_citizen = cls.db.query(User).filter(User.email == "other_citizen@example.com").first()
        if not cls.other_citizen:
            cls.other_citizen = User(
                email="other_citizen@example.com",
                password_hash=hash_password("PlotProof2026!"),
                full_name="Other Citizen",
                role=UserRole.CITIZEN,
                is_active=True,
            )
            cls.db.add(cls.other_citizen)
            cls.db.commit()
            cls.db.refresh(cls.other_citizen)
        cls.other_citizen_token = create_access_token(cls.other_citizen.id, cls.other_citizen.role.value)

        cls.created_doc_ids = []
        cls._cleanup_test_docs()

    @classmethod
    def tearDownClass(cls):
        cls._cleanup_test_docs()
        cls.db.close()

    @classmethod
    def _cleanup_test_docs(cls):
        db = SessionLocal()
        try:
            db.query(Document).filter(
                Document.file_name.in_([
                    "survey_142_3a_deed.pdf",
                    "survey_copy.pdf",
                    "huge_deed.pdf",
                    "fake_deed.pdf",
                    "malicious_script.exe",
                    "infected_deed.pdf"
                ])
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()


    def test_01_upload_valid_pdf(self):
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Land Sale Deed 142/3A) >>\nendobj\ntrailer\n<< >>\n%%EOF\n"
        files = {
            "file": ("survey_142_3a_deed.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 201, res.text)
        data = res.json()

        self.assertIn("document_id", data)
        self.assertEqual(data["file_name"], "survey_142_3a_deed.pdf")
        self.assertEqual(data["mime_type"], "application/pdf")
        self.assertEqual(len(data["sha256"]), 64)
        self.assertEqual(data["status"], "QUEUED")
        self.assertEqual(data["version"], 1)
        self.assertFalse(data["is_duplicate"])
        self.assertTrue(bool(data["download_url"]))

        doc_id = data["document_id"]
        self.created_doc_ids.append(doc_id)

        # Check DB record & processing job
        db = SessionLocal()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            self.assertIsNotNone(doc)
            self.assertEqual(doc.owner_user_id, self.citizen.id)

            job = db.query(ProcessingJob).filter(ProcessingJob.document_id == doc_id).first()
            self.assertIsNotNone(job)
            self.assertEqual(job.job_type, "OCR")
            self.assertEqual(job.status.value, "PENDING")
            self.assertEqual(job.attempts, 0)
        finally:
            db.close()

        print("[PASS] Test 1: Valid PDF Ingestion, Metadata & OCR Job Queueing Verified")

    def test_02_invalid_extension_rejected(self):
        fake_exe = b"MZ\x90\x00\x03\x00\x00\x00"
        files = {
            "file": ("malicious_script.exe", io.BytesIO(fake_exe), "application/x-msdownload")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 400)
        err = res.json()["detail"]
        self.assertEqual(err["code"], "UNSUPPORTED_FILE_TYPE")
        print("[PASS] Test 2: Invalid File Extension Rejection (400) Verified")

    def test_03_invalid_magic_bytes_rejected(self):
        # Named .pdf but contains arbitrary plain text without PDF signature
        corrupted_bytes = b"Hello world this is not a valid PDF file"
        files = {
            "file": ("fake_deed.pdf", io.BytesIO(corrupted_bytes), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 400)
        err = res.json()["detail"]
        self.assertEqual(err["code"], "UNSUPPORTED_FILE_TYPE")
        print("[PASS] Test 3: Magic Bytes / File Signature Mismatch Rejection (400) Verified")

    def test_04_oversized_file_rejected(self):
        # 51 MB simulated oversized payload
        oversized = io.BytesIO(b"%PDF" + b"0" * (51 * 1024 * 1024))
        files = {
            "file": ("huge_deed.pdf", oversized, "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 400)
        err = res.json()["detail"]
        self.assertEqual(err["code"], "FILE_TOO_LARGE")
        self.assertIn("50 MB", err["message"])
        print("[PASS] Test 4: Oversized Document (>50MB) Hard Limit Rejection (400) Verified")

    def test_05_malware_detection(self):
        eicar_string = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        infected_pdf = b"%PDF-1.4\n" + eicar_string + b"\n%%EOF"
        files = {
            "file": ("infected_deed.pdf", io.BytesIO(infected_pdf), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 400)
        err = res.json()["detail"]
        self.assertEqual(err["code"], "MALWARE_DETECTED")
        print("[PASS] Test 5: Malware & EICAR Signature Detection (400) Verified")

    def test_06_duplicate_file_detection(self):
        # Upload exact same binary content as test 1
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Title (Land Sale Deed 142/3A) >>\nendobj\ntrailer\n<< >>\n%%EOF\n"
        files = {
            "file": ("survey_copy.pdf", io.BytesIO(pdf_content), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertTrue(data["is_duplicate"])
        self.created_doc_ids.append(data["document_id"])
        print("[PASS] Test 6: SHA-256 Duplicate File Fingerprint Detection Verified")

    def test_07_document_versioning(self):
        # Upload new revision with same file_name
        revised_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (Land Sale Deed 142/3A - Rev 2) >>\nendobj\ntrailer\n<< >>\n%%EOF\n"
        files = {
            "file": ("survey_142_3a_deed.pdf", io.BytesIO(revised_pdf), "application/pdf")
        }
        headers = {"Authorization": f"Bearer {self.citizen_token}"}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data["version"], 2)
        self.created_doc_ids.append(data["document_id"])
        print("[PASS] Test 7: Immutable Document Versioning (v1 -> v2) Verified")

    def test_08_status_query(self):
        doc_id = self.created_doc_ids[0]
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.get(f"/api/v1/documents/{doc_id}/status", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["document_id"], doc_id)
        self.assertEqual(data["status"], "QUEUED")
        self.assertIsNotNone(data["processing"])
        self.assertEqual(data["processing"]["job_type"], "OCR")
        self.assertEqual(data["processing"]["status"], "PENDING")
        print("[PASS] Test 8: Document Status & Processing Job Lifecycle Query Verified")

    def test_09_download_url_generation(self):
        doc_id = self.created_doc_ids[0]
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.get(f"/api/v1/documents/{doc_id}/download", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["document_id"], doc_id)
        self.assertTrue(bool(data["download_url"]))
        self.assertEqual(data["expires_in_seconds"], 900)
        print("[PASS] Test 9: Temporary Signed Download URL Generation Verified")

    def test_10_unauthorized_user_access_protection(self):
        # Other citizen attempting to access Citizen 1's document
        doc_id = self.created_doc_ids[0]
        headers = {"Authorization": f"Bearer {self.other_citizen_token}"}
        res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        self.assertEqual(res.status_code, 403)
        print("[PASS] Test 10: Unauthorized User Access & Privacy Isolation (403) Verified")

    def test_11_privileged_registrar_access(self):
        # Registrar accessing Citizen 1's document for statutory verification
        doc_id = self.created_doc_ids[0]
        headers = {"Authorization": f"Bearer {self.registrar_token}"}
        res = client.get(f"/api/v1/documents/{doc_id}", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["id"], doc_id)
        print("[PASS] Test 11: Privileged Role (REGISTRAR) Explicit Permission Access Verified")

    def test_12_audit_log_tracking(self):
        # Check audit log for DOCUMENT_UPLOAD action
        db = SessionLocal()
        try:
            log_entry = db.query(AuditLog).filter(
                AuditLog.action == "DOCUMENT_UPLOAD",
                AuditLog.user_id == self.citizen.id
            ).first()
            self.assertIsNotNone(log_entry)
            self.assertEqual(log_entry.resource_type, "document")
            print("[PASS] Test 12: Forensic Security Audit Logging on Ingestion Verified")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
