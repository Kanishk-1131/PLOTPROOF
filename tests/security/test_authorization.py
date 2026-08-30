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
from app.models.user import User, UserRole
from app.models.certificate import Certificate
from app.core.security import create_access_token

client = TestClient(app)


class TestSecurityAuthorization(unittest.TestCase):
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

    def test_01_citizen_forbidden_from_sub_registrar_review(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.post(
            "/api/v1/verifications/PP-2026-000052/review",
            json={"decision": "APPROVED", "remarks": "Unauthorized citizen approval attempt"},
            headers=headers,
        )
        self.assertEqual(res.status_code, 403)
        print("[PASS] Security Test 1: Citizen 403 Forbidden from Sub-Registrar Review Endpoints")

    def test_02_citizen_forbidden_from_revoking_certificates(self):
        db = SessionLocal()
        try:
            cert = db.query(Certificate).first()
            if cert:
                headers = {"Authorization": f"Bearer {self.citizen_token}"}
                res = client.post(
                    f"/api/v1/certificates/{cert.id}/revoke",
                    json={"reason": "Citizen attempting unauthorized certificate revocation"},
                    headers=headers,
                )
                self.assertEqual(res.status_code, 403)
                print("[PASS] Security Test 2: Citizen 403 Forbidden from Certificate Revocation")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
