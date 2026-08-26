import sys
import unittest
from pathlib import Path
from datetime import timedelta

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import init_db
from app.seed_data.seed_db import seed_database
from app.core.security import create_access_token

client = TestClient(app)


class TestSecurityAuthentication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()

    def test_01_invalid_credentials_rejected(self):
        res = client.post("/api/v1/auth/login", json={"email": "citizen@plotproof.gov.in", "password": "WrongPassword123!"})
        self.assertEqual(res.status_code, 401)
        print("[PASS] Security Test 1: Invalid Password Authentication Rejected (401)")

    def test_02_missing_auth_header_rejected(self):
        res = client.get("/api/v1/auth/me")
        self.assertEqual(res.status_code, 401)
        print("[PASS] Security Test 2: Missing Bearer Token Rejection (401)")

    def test_03_expired_jwt_token_rejected(self):
        expired_token = create_access_token(user_id=1, role="CITIZEN", expires_delta=timedelta(seconds=-30))
        headers = {"Authorization": f"Bearer {expired_token}"}
        res = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res.status_code, 401)
        print("[PASS] Security Test 3: Expired JWT Token Rejection (401)")

    def test_04_tampered_jwt_token_rejected(self):
        valid_token = create_access_token(user_id=1, role="CITIZEN")
        parts = valid_token.split(".")
        tampered_token = f"{parts[0]}.eyJyZXF1ZXN0ZWRfcm9sZSI6ICJBRE1JTiJ9.{parts[2]}"
        headers = {"Authorization": f"Bearer {tampered_token}"}
        res = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(res.status_code, 401)
        print("[PASS] Security Test 4: Forged JWT Signature Rejection (401)")



if __name__ == "__main__":
    unittest.main()
