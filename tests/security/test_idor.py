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
from app.models.user import User, UserRole
from app.models.document import Document
from app.core.security import create_access_token, hash_password

client = TestClient(app)


class TestSecurityIDOR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        # Create Citizen A
        cls.user_a = cls.db.query(User).filter(User.email == "citizen_a_idor@test.gov.in").first()
        if not cls.user_a:
            cls.user_a = User(
                email="citizen_a_idor@test.gov.in",
                password_hash=hash_password("Pass123!"),
                full_name="Citizen Alice",
                role=UserRole.CITIZEN,
                is_active=True,
            )
            cls.db.add(cls.user_a)
            cls.db.commit()
            cls.db.refresh(cls.user_a)

        # Create Citizen B
        cls.user_b = cls.db.query(User).filter(User.email == "citizen_b_idor@test.gov.in").first()
        if not cls.user_b:
            cls.user_b = User(
                email="citizen_b_idor@test.gov.in",
                password_hash=hash_password("Pass123!"),
                full_name="Citizen Bob",
                role=UserRole.CITIZEN,
                is_active=True,
            )
            cls.db.add(cls.user_b)
            cls.db.commit()
            cls.db.refresh(cls.user_b)


        cls.token_a = create_access_token(cls.user_a.id, cls.user_a.role.value)
        cls.token_b = create_access_token(cls.user_b.id, cls.user_b.role.value)

        # Citizen A uploads a private deed
        headers_a = {"Authorization": f"Bearer {cls.token_a}"}
        pdf_bytes = b"%PDF-1.4 Alice Confidential Land Deed"
        files = {"file": ("alice_deed.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        res = client.post("/api/v1/documents", files=files, headers=headers_a)
        cls.alice_doc_id = res.json()["document_id"]

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_citizen_b_cannot_access_citizen_a_document(self):
        # Citizen B attempts to access Citizen A's document details
        headers_b = {"Authorization": f"Bearer {self.token_b}"}
        res = client.get(f"/api/v1/documents/{self.alice_doc_id}", headers=headers_b)
        self.assertIn(res.status_code, [403, 404])
        print("[PASS] Security Test 1: IDOR Protection on Document Read (403/404)")

    def test_02_citizen_b_cannot_download_citizen_a_raw_file(self):
        # Citizen B attempts to download Citizen A's deed file
        headers_b = {"Authorization": f"Bearer {self.token_b}"}
        res = client.get(f"/api/v1/documents/{self.alice_doc_id}/download", headers=headers_b)
        self.assertIn(res.status_code, [403, 404])
        print("[PASS] Security Test 2: IDOR Protection on Raw Deed File Download (403/404)")


if __name__ == "__main__":
    unittest.main()
