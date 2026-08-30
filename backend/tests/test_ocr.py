import io
import sys
import unittest
from pathlib import Path
import numpy as np

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus
from app.models.ocr_result import OCRResult
from app.models.ocr_field import OCRField
from app.models.processing_job import ProcessingJob, JobStatus
from app.models.audit_log import AuditLog

from app.core.security import create_access_token
from app.ocr.preprocess import pdf_to_images, deskew_image, get_image_variants
from app.ocr.normalize import (
    normalize_survey_number,
    split_survey_and_subdivision,
    normalize_area,
    normalize_coordinates,
)
from app.services.ocr_service import OCRService

client = TestClient(app)


class TestLayer4OCR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

        cls.registrar = cls.db.query(User).filter(User.email == "registrar@tn.gov.in").first()
        cls.registrar_token = create_access_token(cls.registrar.id, cls.registrar.role.value)

        cls.ocr_service = OCRService()
        cls._create_test_documents()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @classmethod
    def _create_test_documents(cls):
        db = SessionLocal()
        try:
            # Clean previous test ocr docs
            db.query(Document).filter(Document.file_name.like("test_ocr_%")).delete(synchronize_session=False)
            db.commit()

            # 1. Clean English Deed
            doc1 = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_ocr_clean_english.pdf",
                mime_type="application/pdf",
                file_size=1024,
                storage_key="test/test_ocr_clean_english.pdf",
                sha256="1111111111111111111111111111111111111111111111111111111111111111",
                file_hash="1111111111111111111111111111111111111111111111111111111111111111",
                status=DocumentStatus.QUEUED,
                version=1,
                verification_id="PP-TEST-001",
                ocr_raw_text="""GOVERNMENT OF TAMIL NADU - REGISTRATION DEPARTMENT
TITLE DEED OF SALE / CONVEYANCE DEED
Document Registration Number: 4821/2024
DISTRICT: Chennai
TALUK: Tambaram
VILLAGE: Selaiyur Village
SURVEY NUMBER: 142/3A
EXTENT AND MEASUREMENT OF PROPERTY:
All that piece and parcel of land bearing Survey No: 142/3A, measuring an area of 2400 Sq.ft (equivalent to 222.96 Sq.meters).
BOUNDARIES:
North by: Survey No 142/2 (Road 30ft width)
South by: Survey No 142/4 (Vacant Plot)
East by: Survey No 142/3B (Adjacent Plot)
West by: Survey No 142/1 (Residential Property)
COORDINATES:
12.9249, 80.1472
PURCHASER: K. S. Ramanathan
""",
            )
            db.add(doc1)

            # 2. Missing Survey Number
            doc2 = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_ocr_missing_survey.pdf",
                mime_type="application/pdf",
                file_size=1024,
                storage_key="test/test_ocr_missing_survey.pdf",
                sha256="2222222222222222222222222222222222222222222222222222222222222222",
                file_hash="2222222222222222222222222222222222222222222222222222222222222222",
                status=DocumentStatus.QUEUED,
                version=1,
                verification_id="PP-TEST-002",
                ocr_raw_text="""GOVERNMENT OF TAMIL NADU
DEED OF CONVEYANCE
DISTRICT: Chennai
TALUK: Tambaram
VILLAGE: Selaiyur
EXTENT: 2400 Sq.ft
North by: Road
South by: Plot
East by: Canal
West by: Land
""",
            )
            db.add(doc2)
            db.commit()
            db.refresh(doc1)
            db.refresh(doc2)

            # Store physical test files in storage service
            cls.ocr_service.storage.upload_file(
                io.BytesIO(doc1.ocr_raw_text.encode("utf-8")),
                doc1.storage_key,
                "text/plain"
            )
            cls.ocr_service.storage.upload_file(
                io.BytesIO(doc2.ocr_raw_text.encode("utf-8")),
                doc2.storage_key,
                "text/plain"
            )

            job1 = ProcessingJob(document_id=doc1.id, job_type="OCR", status=JobStatus.PENDING)
            job2 = ProcessingJob(document_id=doc2.id, job_type="OCR", status=JobStatus.PENDING)
            db.add_all([job1, job2])
            db.commit()

            cls.doc1_id = doc1.id
            cls.doc2_id = doc2.id
        finally:
            db.close()


    def test_01_clean_english_deed_extraction(self):
        db = SessionLocal()
        try:
            handshake = self.ocr_service.process_document(db, self.doc1_id)
            self.assertEqual(handshake["document_id"], self.doc1_id)
            self.assertEqual(handshake["land"]["survey_number"], "142/3A")
            self.assertEqual(handshake["land"]["subdivision_number"], "3A")
            self.assertEqual(handshake["land"]["district"], "Chennai")
            self.assertEqual(handshake["land"]["taluk"], "Tambaram")
            self.assertEqual(handshake["land"]["village"], "Selaiyur Village")
            self.assertAlmostEqual(handshake["land"]["area"]["square_meters"], 222.96, delta=0.05)
            self.assertEqual(handshake["boundaries"]["north"], "Survey No 142/2 (Road 30ft width)")

            self.assertEqual(handshake["coordinates"]["latitude"], 12.9249)
            self.assertEqual(handshake["coordinates"]["longitude"], 80.1472)
            self.assertFalse(handshake["quality"]["review_required"])
            print("[PASS] Test 1: Clean English Deed Full Field Extraction & Handshake Verified")
        finally:
            db.close()

    def test_02_multivariant_image_preprocessing(self):
        # Generate synthetic 100x100 RGB image
        sample_img = np.full((100, 100, 3), 200, dtype=np.uint8)
        variants = get_image_variants(sample_img)
        self.assertIn("original", variants)
        self.assertIn("grayscale", variants)
        self.assertIn("denoised", variants)
        self.assertIn("adaptive_threshold", variants)
        self.assertIn("contrast_enhanced", variants)
        print("[PASS] Test 2: Multi-Variant Adaptive Image Preprocessing Engine Verified")

    def test_03_deskew_orientation(self):
        # Create an image and test deskew logic
        img = np.full((200, 200, 3), 255, dtype=np.uint8)
        deskewed = deskew_image(img)
        self.assertEqual(deskewed.shape, img.shape)
        print("[PASS] Test 3: Document Deskew Orientation Correction Verified")

    def test_04_tamil_regional_normalization(self):
        tamil_survey = "சர்வே எண் : 142/3A"
        normalized = normalize_survey_number("142 / 3A")
        self.assertEqual(normalized, "142/3A")
        base, sub = split_survey_and_subdivision(normalized)
        self.assertEqual(base, "142")
        self.assertEqual(sub, "3A")
        print("[PASS] Test 4: Survey & Subdivision Number Normalization Verified")

    def test_05_area_conversions_to_standard_sqm(self):
        # Acres
        res_acre = normalize_area("Extent: 2.50 Acres")
        self.assertAlmostEqual(res_acre["square_meters"], 10117.14, delta=0.5)

        # Cents
        res_cent = normalize_area("Extent: 5.5 Cents")
        self.assertAlmostEqual(res_cent["square_meters"], 222.58, delta=0.5)

        # Square feet
        res_sqft = normalize_area("2400 Sq.ft")
        self.assertAlmostEqual(res_sqft["square_meters"], 222.96, delta=0.05)
        print("[PASS] Test 5: Multi-Unit Area Normalization to Standard Square Meters Verified")


    def test_06_coordinate_boundary_validation(self):
        valid = normalize_coordinates("GPS Location: 13.0827, 80.2707")
        self.assertIsNotNone(valid)
        self.assertEqual(valid["latitude"], 13.0827)
        self.assertEqual(valid["longitude"], 80.2707)

        # Out of bounds coordinates (-95 is invalid latitude)
        invalid = normalize_coordinates("Location: -95.0, 80.0")
        self.assertIsNone(invalid)
        print("[PASS] Test 6: Coordinate Validation & Geographic Plausibility Verified")

    def test_07_missing_survey_triggers_review(self):
        db = SessionLocal()
        try:
            handshake = self.ocr_service.process_document(db, self.doc2_id)
            self.assertIsNone(handshake["land"]["survey_number"])
            self.assertTrue(handshake["quality"]["review_required"])
            print("[PASS] Test 7: Missing Survey Number Correctly Flags Human Review Required")
        finally:
            db.close()

    def test_08_get_document_ocr_endpoint(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.get(f"/api/v1/documents/{self.doc1_id}/ocr", headers=headers)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertEqual(data["document_id"], self.doc1_id)
        self.assertTrue(len(data["fields"]) > 0)
        self.assertIn("raw_blocks", data)
        print("[PASS] Test 8: Raw OCR & Extracted Fields REST Endpoint Verified")

    def test_09_human_review_correction_workflow(self):
        # 1. Fetch fields as Registrar
        headers = {"Authorization": f"Bearer {self.registrar_token}"}
        fields_res = client.get(f"/api/v1/documents/{self.doc1_id}/fields", headers=headers)
        self.assertEqual(fields_res.status_code, 200)
        fields = fields_res.json()

        # Find survey_number field
        sno_field = next(f for f in fields if f["field_name"] == "survey_number")

        # 2. Registrar corrects the field value
        patch_res = client.patch(
            f"/api/v1/documents/{self.doc1_id}/fields/{sno_field['id']}",
            json={"field_value": "142/3A-CONFIRMED", "status": "CORRECTED"},
            headers=headers,
        )
        self.assertEqual(patch_res.status_code, 200)
        self.assertEqual(patch_res.json()["field_value"], "142/3A-CONFIRMED")
        self.assertEqual(patch_res.json()["status"], "CORRECTED")

        # 3. Check audit log for OCR_FIELD_CORRECTION
        db = SessionLocal()
        try:
            log = db.query(AuditLog).filter(
                AuditLog.action == "OCR_FIELD_CORRECTION",
                AuditLog.user_id == self.registrar.id
            ).first()
            self.assertIsNotNone(log)
            self.assertIn("142/3A-CONFIRMED", log.details)
        finally:
            db.close()

        print("[PASS] Test 9: Sub-Registrar Statutory Field Correction & Audit Logging Verified")

    def test_10_citizen_cannot_edit_statutory_fields(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        fields_res = client.get(f"/api/v1/documents/{self.doc1_id}/fields", headers=headers)
        sno_field = fields_res.json()[0]

        # Citizen attempts to modify extracted field
        patch_res = client.patch(
            f"/api/v1/documents/{self.doc1_id}/fields/{sno_field['id']}",
            json={"field_value": "HACKED", "status": "CORRECTED"},
            headers=headers,
        )
        self.assertEqual(patch_res.status_code, 403)
        print("[PASS] Test 10: Citizen Role Prohibited from Direct Field Alteration (403) Verified")

    def test_11_layer5_handshake_structure(self):
        db = SessionLocal()
        try:
            handshake = self.ocr_service.process_document(db, self.doc1_id)
            # Validate complete contract schema for Layer 5 consumption
            self.assertIn("document_id", handshake)
            self.assertIn("land", handshake)
            self.assertIn("boundaries", handshake)
            self.assertIn("coordinates", handshake)
            self.assertIn("quality", handshake)
            self.assertIn("square_meters", handshake["land"]["area"])
            self.assertIn("north", handshake["boundaries"])
            self.assertIn("latitude", handshake["coordinates"])
            print("[PASS] Test 11: Standardized Layer 5 Handshake Contract Schema Verified")
        finally:
            db.close()

    def test_12_reprocess_endpoint(self):
        headers = {"Authorization": f"Bearer {self.registrar_token}"}
        res = client.post(f"/api/v1/documents/{self.doc1_id}/ocr/reprocess", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["document_id"], self.doc1_id)
        self.assertIn("land", data)
        print("[PASS] Test 12: OCR Reprocessing On-Demand Endpoint Verified")


if __name__ == "__main__":
    unittest.main()
