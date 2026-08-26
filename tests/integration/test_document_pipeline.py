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
from app.models.processing_job import ProcessingJob
from app.core.security import create_access_token

client = TestClient(app)


class TestIntegrationDocumentPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()
        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_upload_and_processing_job_queueing(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        pdf_content = b"%PDF-1.4 Integration Pipeline Test Deed Survey 142/3A " + uuid.uuid4().bytes
        files = {"file": ("integ_deed.pdf", io.BytesIO(pdf_content), "application/pdf")}

        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("document_id", data)
        self.assertEqual(data["file_name"], "integ_deed.pdf")
        self.assertEqual(data["status"], "QUEUED")

        # Verify processing job queued
        db = SessionLocal()
        try:
            job = db.query(ProcessingJob).filter(ProcessingJob.document_id == data["document_id"]).first()
            self.assertIsNotNone(job)
            self.assertEqual(job.job_type, "OCR")
            print("[PASS] Integration Test 1: Document Upload & OCR Processing Job Queueing")
        finally:
            db.close()

    def test_02_duplicate_document_versioning(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        fname = f"version_{uuid.uuid4().hex[:6]}.pdf"
        unique_bytes = b"%PDF-1.4 Versioning Test Unique " + uuid.uuid4().bytes
        files_v1 = {"file": (fname, io.BytesIO(unique_bytes), "application/pdf")}

        res_v1 = client.post("/api/v1/documents", files=files_v1, headers=headers)
        self.assertEqual(res_v1.status_code, 201)
        self.assertEqual(res_v1.json()["version"], 1)

        # Upload exact same file -> detects duplicate hash and creates version 2
        files_v2 = {"file": (fname, io.BytesIO(unique_bytes), "application/pdf")}
        res_v2 = client.post("/api/v1/documents", files=files_v2, headers=headers)
        self.assertEqual(res_v2.status_code, 201)
        self.assertEqual(res_v2.json()["version"], 2)
        print("[PASS] Integration Test 2: Immutable Document Versioning (v1 -> v2) Verified")



if __name__ == "__main__":
    unittest.main()
