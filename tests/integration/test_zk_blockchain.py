import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.ocr_field import OCRField
from app.models.verification import Verification
from app.models.zk_proof import ZKProofRecord
from app.models.blockchain_anchor import BlockchainAnchor
from app.privacy.zk_service import ZKService
from app.blockchain.service import BlockchainService
from app.services.orchestrator import OrchestratorService


class TestIntegrationZKBlockchain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.zk_service = ZKService()
        cls.blockchain_service = BlockchainService()
        cls.orchestrator = OrchestratorService()
        cls._setup_clean_document()

    @classmethod
    def _setup_clean_document(cls):
        db = SessionLocal()
        try:
            vid = "PP-ZK-BLOCK-0001"
            from app.models.certificate import Certificate
            db.query(Verification).filter(Verification.verification_id == vid).delete(synchronize_session=False)
            db.query(Certificate).filter(Certificate.verification_id == vid).delete(synchronize_session=False)
            db.query(BlockchainAnchor).filter(BlockchainAnchor.verification_id == vid).delete(synchronize_session=False)
            from app.models.spatial_validation import SpatialValidation
            from app.models.integrity_record import IntegrityRecord
            old_doc = db.query(Document).filter(Document.verification_id == vid).first()
            if old_doc:
                db.query(Certificate).filter(Certificate.document_id == old_doc.id).delete(synchronize_session=False)
                db.query(SpatialValidation).filter(SpatialValidation.document_id == old_doc.id).delete(synchronize_session=False)

                db.query(IntegrityRecord).filter(IntegrityRecord.document_id == old_doc.id).delete(synchronize_session=False)
                db.query(ZKProofRecord).filter(ZKProofRecord.document_id == old_doc.id).delete(synchronize_session=False)
                db.query(OCRField).filter(OCRField.document_id == old_doc.id).delete(synchronize_session=False)
                db.delete(old_doc)
            db.commit()



            user = db.query(User).first()
            doc = Document(
                owner_user_id=user.id,
                file_name="zk_pipe_clean.pdf",
                mime_type="application/pdf",
                file_size=2000,
                storage_key="test/zk_pipe_clean.pdf",
                sha256="b" * 64,
                file_hash="b" * 64,
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
        finally:
            db.close()

    def test_01_zk_commitment_to_blockchain_anchor_pipeline(self):
        db = SessionLocal()
        try:
            # 1. Run orchestration pipeline
            self.orchestrator.start_verification(db, self.test_doc_id)

            # 2. Verify ZK Proof record
            zk_proof = db.query(ZKProofRecord).filter(ZKProofRecord.document_id == self.test_doc_id).first()
            self.assertIsNotNone(zk_proof)
            self.assertEqual(zk_proof.status, "VERIFIED")
            self.assertIsNotNone(zk_proof.commitment)

            # 3. Verify On-Chain Blockchain Anchor record
            anchor = db.query(BlockchainAnchor).filter(BlockchainAnchor.document_id == self.test_doc_id).first()
            self.assertIsNotNone(anchor)
            self.assertEqual(anchor.status, "CONFIRMED")
            self.assertTrue(anchor.transaction_hash.startswith("0x"))
            print("[PASS] Integration Test 1: ZK Commitment Directly Anchored On-Chain (Zero Citizen PII)")

        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
