import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.ocr.normalize import (
    normalize_survey_number,
    normalize_area,
    normalize_coordinates,
)


class TestUnitOCR(unittest.TestCase):
    """
    Layer 12: Unit tests for OCR Document Intelligence & Normalizers.
    """

    def test_01_survey_number_normalization(self):
        # Clean formatting
        self.assertEqual(normalize_survey_number("Survey No. 142 / 3A"), "142/3A")
        self.assertEqual(normalize_survey_number("புல எண்: 142/3A"), "142/3A")
        self.assertEqual(normalize_survey_number("S.F. 58/2B1"), "58/2B1")
        self.assertEqual(normalize_survey_number(""), "")
        print("[PASS] Unit Test 1: Survey & Subdivision Number Normalization")

    def test_02_area_normalization_multi_units(self):
        # Convert multi-units to standard square meters
        # 2400 sq.ft -> ~222.96 sq.m
        res_ft = normalize_area("2400 Sq.ft")
        self.assertIsNotNone(res_ft["square_meters"])
        self.assertAlmostEqual(res_ft["square_meters"], 222.96, delta=0.5)

        # 1 Acre -> 4046.86 sq.m
        res_acre = normalize_area("1 Acre")
        self.assertIsNotNone(res_acre["square_meters"])
        self.assertAlmostEqual(res_acre["square_meters"], 4046.86, delta=1.0)

        # 5 Cents -> 202.34 sq.m
        res_cents = normalize_area("5 Cents")
        self.assertIsNotNone(res_cents["square_meters"])
        self.assertAlmostEqual(res_cents["square_meters"], 202.34, delta=0.5)
        print("[PASS] Unit Test 2: Multi-Unit Area Normalization to Standard Square Meters")

    def test_03_coordinate_geographic_plausibility(self):
        # Valid GPS coordinates
        coords_valid = normalize_coordinates("12.9252, 80.1475")
        self.assertIsNotNone(coords_valid)
        self.assertEqual(coords_valid["latitude"], 12.9252)
        self.assertEqual(coords_valid["longitude"], 80.1475)

        # Implausible or unparseable coordinates
        coords_invalid = normalize_coordinates("not coordinates")
        self.assertIsNone(coords_invalid)
        print("[PASS] Unit Test 3: GPS Coordinate Extraction & Range Normalization")



if __name__ == "__main__":
    unittest.main()
