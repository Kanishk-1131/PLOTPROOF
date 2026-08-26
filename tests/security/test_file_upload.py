import io
import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User
from app.core.security import create_access_token

client = TestClient(app)


class TestSecurityFileUpload(unittest.TestCase):
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

    def test_01_executable_file_rejected(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        exe_content = b"MZ\x90\x00\x03\x00\x00\x00Malicious Executable Payload"
        files = {"file": ("malware.exe", io.BytesIO(exe_content), "application/x-msdownload")}
        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 400)
        print("[PASS] Security Test 1: Executable (.exe) Upload Rejected (400)")

    def test_02_script_file_rejected(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        sh_content = b"#!/bin/bash\nrm -rf /"
        files = {"file": ("attack.sh", io.BytesIO(sh_content), "text/x-shellscript")}
        res = client.post("/api/v1/documents", files=files, headers=headers)
        self.assertEqual(res.status_code, 400)
        print("[PASS] Security Test 2: Shell Script (.sh) Upload Rejected (400)")

    def test_03_polyglot_mismatched_mime_rejected(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        # Fake PDF extension with executable contents
        fake_pdf = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 50
        files = {"file": ("polyglot.pdf", io.BytesIO(fake_pdf), "application/pdf")}
        res = client.post("/api/v1/documents", files=files, headers=headers)
        # Magic bytes sniffing detects non-PDF/non-image header
        self.assertEqual(res.status_code, 400)
        print("[PASS] Security Test 3: Magic Bytes Polyglot File Header Sniffing & Rejection (400)")


if __name__ == "__main__":
    unittest.main()
