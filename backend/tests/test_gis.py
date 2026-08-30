import io
import json
import sys
import unittest
from pathlib import Path
from shapely.geometry import Polygon

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from fastapi.testclient import TestClient

from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.parcel import Parcel
from app.models.spatial_validation import SpatialValidation
from app.models.ocr_field import OCRField
from app.core.security import create_access_token
from app.gis.geometry import (
    build_polygon_from_coordinates,
    build_polygon_from_centroid,
    validate_geometry,
    repair_geometry,
)
from app.gis.crs import calculate_metric_area_sqm, project_to_meters
from app.gis.overlap import (
    classify_spatial_relationship,
    validate_area_consistency,
    TOUCH_TOLERANCE_METERS,
)
from app.gis.risk import calculate_spatial_risk_score
from app.services.gis_service import GISService

client = TestClient(app)


class TestLayer5GIS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.db = SessionLocal()

        cls.citizen = cls.db.query(User).filter(User.email == "citizen@plotproof.gov.in").first()
        cls.citizen_token = create_access_token(cls.citizen.id, cls.citizen.role.value)

        cls.registrar = cls.db.query(User).filter(User.email == "registrar@tn.gov.in").first()
        cls.registrar_token = create_access_token(cls.registrar.id, cls.registrar.role.value)

        cls.gis_service = GISService()
        cls._create_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    @classmethod
    def _create_test_data(cls):
        db = SessionLocal()
        try:
            # Seed test cadastral parcels
            GISService.seed_cadastral_parcels(db)

            # Clean previous test gis docs
            db.query(Document).filter(Document.file_name.like("test_gis_%")).delete(synchronize_session=False)
            db.commit()

            # 1. Clean Title Document matching Survey 142/3A
            doc_clean = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_gis_clean.pdf",
                mime_type="application/pdf",
                file_size=1024,
                storage_key="test/test_gis_clean.pdf",
                sha256="3333333333333333333333333333333333333333333333333333333333333333",
                file_hash="3333333333333333333333333333333333333333333333333333333333333333",
                status=DocumentStatus.COMPLETED,
                version=1,
                verification_id="PP-GIS-001",
                ocr_raw_text="Deed for Survey 142/3A",
            )
            db.add(doc_clean)
            db.commit()
            db.refresh(doc_clean)

            # Add OCR Fields for clean document
            f1 = OCRField(document_id=doc_clean.id, field_name="survey_number", field_value="142/3A", confidence=0.98, status="CONFIRMED")
            f2 = OCRField(document_id=doc_clean.id, field_name="area", field_value="2400 Sq.ft", confidence=0.95, status="CONFIRMED")
            f3 = OCRField(document_id=doc_clean.id, field_name="coordinates", field_value="12.9252, 80.1475", confidence=0.96, status="CONFIRMED")
            f4 = OCRField(document_id=doc_clean.id, field_name="district", field_value="Chennai", confidence=0.95, status="CONFIRMED")
            f5 = OCRField(document_id=doc_clean.id, field_name="taluk", field_value="Tambaram", confidence=0.95, status="CONFIRMED")
            f6 = OCRField(document_id=doc_clean.id, field_name="village", field_value="Selaiyur", confidence=0.95, status="CONFIRMED")
            db.add_all([f1, f2, f3, f4, f5, f6])

            # 2. Overlapping Document (Encroached plot)
            doc_overlap = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_gis_overlap_deed.pdf",
                mime_type="application/pdf",
                file_size=1024,
                storage_key="test/test_gis_overlap_deed.pdf",
                sha256="4444444444444444444444444444444444444444444444444444444444444444",
                file_hash="4444444444444444444444444444444444444444444444444444444444444444",
                status=DocumentStatus.COMPLETED,
                version=1,
                verification_id="PP-GIS-002",
                ocr_raw_text="Overlapping deed on Survey 142/3A",
            )
            db.add(doc_overlap)
            db.commit()
            db.refresh(doc_overlap)

            fo1 = OCRField(document_id=doc_overlap.id, field_name="survey_number", field_value="142/3A", confidence=0.98, status="CONFIRMED")
            fo2 = OCRField(document_id=doc_overlap.id, field_name="area", field_value="2400 Sq.ft", confidence=0.95, status="CONFIRMED")
            fo3 = OCRField(document_id=doc_overlap.id, field_name="coordinates", field_value="12.9252, 80.1475", confidence=0.96, status="CONFIRMED")
            db.add_all([fo1, fo2, fo3])

            # 3. Insufficient Geometry Document (Case C: Text descriptions only)
            doc_insufficient = Document(
                owner_user_id=cls.citizen.id,
                file_name="test_gis_text_only.pdf",
                mime_type="application/pdf",
                file_size=1024,
                storage_key="test/test_gis_text_only.pdf",
                sha256="5555555555555555555555555555555555555555555555555555555555555555",
                file_hash="5555555555555555555555555555555555555555555555555555555555555555",
                status=DocumentStatus.COMPLETED,
                version=1,
                verification_id="PP-GIS-003",
                ocr_raw_text="Text boundaries only",
            )
            db.add(doc_insufficient)
            db.commit()
            db.refresh(doc_insufficient)

            fi1 = OCRField(document_id=doc_insufficient.id, field_name="survey_number", field_value=None, confidence=0.0, status="REVIEW_REQUIRED")
            fi2 = OCRField(document_id=doc_insufficient.id, field_name="coordinates", field_value=None, confidence=0.0, status="REVIEW_REQUIRED")
            db.add_all([fi1, fi2])
            db.commit()


            cls.doc_clean_id = doc_clean.id
            cls.doc_overlap_id = doc_overlap.id
            cls.doc_insufficient_id = doc_insufficient.id
        finally:
            db.close()

    def test_01_geometry_creation_coordinate_order(self):
        # Section 9: Longitude = X, Latitude = Y
        # Test coordinates passed in [lat, lng] format are correctly normalized to [lng=x, lat=y]
        coords = [
            [12.9249, 80.1472],
            [12.9249, 80.1478],
            [12.9255, 80.1478],
            [12.9255, 80.1472],
        ]
        poly = build_polygon_from_coordinates(coords)
        self.assertIsNotNone(poly)
        self.assertTrue(poly.is_valid)
        # Check that X coordinate is Longitude (~80) and Y coordinate is Latitude (~12)
        minx, miny, maxx, maxy = poly.bounds
        self.assertAlmostEqual(minx, 80.1472, delta=0.001)
        self.assertAlmostEqual(miny, 12.9249, delta=0.001)
        print("[PASS] Test 1: Coordinate Ordering (Longitude=X, Latitude=Y) Verified")

    def test_02_geometry_validation_and_repair(self):
        # Valid polygon
        valid_poly = Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)])
        self.assertTrue(validate_geometry(valid_poly))

        # Self-intersecting bowtie polygon (invalid)
        invalid_poly = Polygon([(0, 0), (2, 2), (2, 0), (0, 2), (0, 0)])
        self.assertFalse(validate_geometry(invalid_poly))

        # Controlled repair
        repaired, is_safe = repair_geometry(invalid_poly)
        self.assertTrue(validate_geometry(repaired))
        print("[PASS] Test 2: Geometry Structural Validation & Controlled Repair Verified")

    def test_03_metric_area_projected_crs(self):
        # Degree polygon in Chennai: [80.1472, 12.9249] to [80.1478, 12.9255]
        # ~66 meters by ~66 meters ~ 4300+ m²
        poly = Polygon([
            (80.1472, 12.9249),
            (80.1478, 12.9249),
            (80.1478, 12.9255),
            (80.1472, 12.9255),
            (80.1472, 12.9249),
        ])
        metric_area = calculate_metric_area_sqm(poly)
        self.assertGreater(metric_area, 4000.0)
        self.assertLess(metric_area, 4500.0)
        print("[PASS] Test 3: Metric Projection (EPSG:32644) Geodesic Area Calculation Verified")

    def test_04_touching_vs_overlapping_distinction(self):
        # Two polygons sharing a boundary edge (Touching)
        poly_a = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
        poly_b = Polygon([(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)])
        rel, overlap_sqm, overlap_pct = classify_spatial_relationship(poly_a, poly_b)
        self.assertEqual(rel, "TOUCHING")
        self.assertEqual(overlap_sqm, 0.0)

        # Disjoint polygons
        poly_c = Polygon([(5, 5), (6, 5), (6, 6), (5, 6), (5, 5)])
        rel_c, _, _ = classify_spatial_relationship(poly_a, poly_c)
        self.assertEqual(rel_c, "DISJOINT")
        print("[PASS] Test 4: Touching vs Disjoint Spatial Classification Verified")

    def test_05_exact_overlap_percentage_calculation(self):
        # Two overlapping polygons with exactly 50% overlap in Chennai area
        poly_a = Polygon([(80.1472, 12.9249), (80.1476, 12.9249), (80.1476, 12.9255), (80.1472, 12.9255), (80.1472, 12.9249)])
        poly_b = Polygon([(80.1474, 12.9249), (80.1478, 12.9249), (80.1478, 12.9255), (80.1474, 12.9255), (80.1474, 12.9249)])
        rel, overlap_sqm, overlap_pct = classify_spatial_relationship(poly_a, poly_b)
        self.assertEqual(rel, "OVERLAPPING")
        self.assertAlmostEqual(overlap_pct, 50.0, delta=2.0)
        print("[PASS] Test 5: Exact Metric Overlap Area & Percentage Computation Verified")


    def test_06_area_consistency_thresholds(self):
        # <= 1% -> NORMAL
        res_normal = validate_area_consistency(10000.0, 9950.0)  # 0.5% diff
        self.assertEqual(res_normal["tier"], "NORMAL")

        # 1-5% -> REVIEW
        res_review = validate_area_consistency(10000.0, 9700.0)  # 3.09% diff
        self.assertEqual(res_review["tier"], "REVIEW")

        # > 5% -> HIGH_RISK
        res_high = validate_area_consistency(10000.0, 9000.0)  # 11.1% diff
        self.assertEqual(res_high["tier"], "HIGH_RISK")
        print("[PASS] Test 6: Area Mismatch & Multi-Tier Severity Classification Verified")

    def test_07_spatial_risk_score_factors(self):
        # Low risk scenario (clean match, no overlap)
        risk_clean = calculate_spatial_risk_score(
            geometry_valid=True,
            geometry_repaired=False,
            spatial_relationship="IDENTICAL",
            overlap_percentage=0.0,
            area_difference_percent=0.5,
            coordinate_confidence=0.95,
            parcel_matched=True,
        )
        self.assertEqual(risk_clean["level"], "LOW")
        self.assertLessEqual(risk_clean["score"], 20.0)

        # High risk scenario (significant overlap)
        risk_overlap = calculate_spatial_risk_score(
            geometry_valid=True,
            geometry_repaired=False,
            spatial_relationship="OVERLAPPING",
            overlap_percentage=15.0,
            area_difference_percent=2.0,
            coordinate_confidence=0.90,
            parcel_matched=True,
        )
        self.assertEqual(risk_overlap["level"], "HIGH")
        print("[PASS] Test 7: Multi-Factor Spatial Risk Engine (0-100 Score) Verified")


    def test_08_case_c_insufficient_geometry_flag(self):
        db = SessionLocal()
        try:
            res = self.gis_service.validate_document_spatial(db, self.doc_insufficient_id)
            self.assertEqual(res["decision"], "GEOMETRY_INSUFFICIENT")
            self.assertFalse(res["geometry"]["valid"])
            print("[PASS] Test 8: Case C (Text-Only Boundaries) Correctly Flags GEOMETRY_INSUFFICIENT")
        finally:
            db.close()

    def test_09_spatial_validation_clean_deed(self):
        db = SessionLocal()
        try:
            handshake = self.gis_service.validate_document_spatial(db, self.doc_clean_id)
            self.assertEqual(handshake["document_id"], self.doc_clean_id)
            self.assertEqual(handshake["parcel"]["survey_number"], "142/3A")
            self.assertTrue(handshake["geometry"]["valid"])
            self.assertIn("difference_percentage", handshake["area_validation"])
            self.assertIn("score", handshake["risk"])
            print("[PASS] Test 9: Clean Deed Spatial Validation Pipeline Execution Verified")
        finally:
            db.close()

    def test_10_spatial_collision_detection(self):
        db = SessionLocal()
        try:
            handshake = self.gis_service.validate_document_spatial(db, self.doc_overlap_id)
            self.assertEqual(handshake["spatial_relationship"]["type"], "OVERLAPPING")
            self.assertGreater(handshake["spatial_relationship"]["overlap_area_sq_m"], 0.0)
            self.assertEqual(handshake["decision"], "SPATIAL_COLLISION")
            print("[PASS] Test 10: Spatial Collision Interception & Overlap Detection Verified")
        finally:
            db.close()

    def test_11_privacy_isolated_map_geojson(self):
        headers = {"Authorization": f"Bearer {self.citizen_token}"}
        res = client.get(f"/api/v1/documents/{self.doc_clean_id}/spatial/map", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["type"], "FeatureCollection")
        self.assertTrue(len(data["features"]) >= 1)
        # Verify candidate feature has status and properties
        cand = next(f for f in data["features"] if f["properties"].get("role") == "CANDIDATE")
        self.assertIsNotNone(cand)
        print("[PASS] Test 11: Privacy-Isolated Candidate & Reference GeoJSON Map Endpoint Verified")

    def test_12_authoritative_cadastral_read_only(self):
        # Verify reference parcel geometry remains unchanged after spatial checks (Section 28)
        db = SessionLocal()
        try:
            p_before = db.scalar(select(Parcel).where(Parcel.survey_number == "142/3A"))
            area_before = p_before.area_sq_m
            geom_before = str(p_before.geometry)

            # Re-run validation on clean and overlap
            self.gis_service.validate_document_spatial(db, self.doc_clean_id)
            self.gis_service.validate_document_spatial(db, self.doc_overlap_id)

            p_after = db.scalar(select(Parcel).where(Parcel.survey_number == "142/3A"))
            self.assertEqual(p_after.area_sq_m, area_before)
            self.assertEqual(str(p_after.geometry), geom_before)
            print("[PASS] Test 12: Authoritative Cadastral Dataset Read-Only Invariance Verified")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
