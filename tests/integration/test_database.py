import sys
import unittest
import uuid
from pathlib import Path
from sqlalchemy.exc import IntegrityError

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus
from app.models.verification import Verification


class TestIntegrationDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()

    def test_01_unique_verification_id_constraint(self):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            vid = f"PP-UNIQUE-{uuid.uuid4().hex[:6].upper()}"
            doc1 = Document(
                owner_user_id=user.id,
                file_name="db_test1.pdf",
                mime_type="application/pdf",
                file_size=100,
                storage_key=f"test/{vid}_1.pdf",
                sha256="d" * 64,
                file_hash="d" * 64,
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id=vid,
            )
            db.add(doc1)
            db.commit()

            # Attempt duplicate document with same verification_id
            doc2 = Document(
                owner_user_id=user.id,
                file_name="db_test2.pdf",
                mime_type="application/pdf",
                file_size=100,
                storage_key=f"test/{vid}_2.pdf",
                sha256="e" * 64,
                file_hash="e" * 64,
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id=vid,
            )
            db.add(doc2)
            with self.assertRaises(IntegrityError):
                db.commit()
            db.rollback()
            print("[PASS] Integration Test 1: Unique Verification ID Constraint Enforced")
        finally:
            db.close()

    def test_02_cascade_delete_integrity(self):
        db = SessionLocal()
        try:
            user = db.query(User).first()
            vid = f"PP-CASCADE-{uuid.uuid4().hex[:6].upper()}"
            doc = Document(
                owner_user_id=user.id,
                file_name="cascade_test.pdf",
                mime_type="application/pdf",
                file_size=100,
                storage_key=f"test/{vid}.pdf",
                sha256="f" * 64,
                file_hash="f" * 64,
                status=DocumentStatus.PROCESSING,
                version=1,
                verification_id=vid,
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            verif = Verification(
                verification_id=vid,
                document_id=doc.id,
                status="PROCESSING",
                current_stage="DOCUMENT",
            )
            db.add(verif)
            db.commit()

            # Deleting document cascades to verification
            db.delete(doc)
            db.commit()

            orphaned_verif = db.query(Verification).filter(Verification.verification_id == vid).first()
            self.assertIsNone(orphaned_verif)
            print("[PASS] Integration Test 2: Foreign Key Cascade Deletion Verified")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
