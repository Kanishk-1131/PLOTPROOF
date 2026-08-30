import sys
import unittest
from pathlib import Path
from shapely.geometry import Polygon

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.gis.geometry import validate_geometry
from app.gis.crs import calculate_metric_area_sqm
from app.gis.overlap import classify_spatial_relationship


class TestUnitGIS(unittest.TestCase):
    """
    Layer 12: Unit tests for Spatial Topological Engine & Known Polygon Validation.
    """

    def test_01_known_polygons_no_overlap(self):
        # Section 4: Test A — No overlap (Disjoint)
        poly_a = Polygon([(80.1470, 12.9250), (80.1480, 12.9250), (80.1480, 12.9260), (80.1470, 12.9260), (80.1470, 12.9250)])
        poly_b = Polygon([(80.1490, 12.9250), (80.1500, 12.9250), (80.1500, 12.9260), (80.1490, 12.9260), (80.1490, 12.9250)])

        relationship, overlap_sqm, overlap_pct = classify_spatial_relationship(poly_a, poly_b)
        self.assertEqual(relationship, "DISJOINT")
        self.assertEqual(overlap_sqm, 0.0)
        self.assertEqual(overlap_pct, 0.0)
        print("[PASS] Unit Test 1: Known Polygons Test A — Disjoint (No Overlap) Confirmed")

    def test_02_known_polygons_with_overlap(self):
        # Section 4: Test B — Overlap
        poly_a = Polygon([(80.1470, 12.9250), (80.1485, 12.9250), (80.1485, 12.9260), (80.1470, 12.9260), (80.1470, 12.9250)])
        poly_b = Polygon([(80.1480, 12.9250), (80.1495, 12.9250), (80.1495, 12.9260), (80.1480, 12.9260), (80.1480, 12.9250)])

        relationship, overlap_sqm, overlap_pct = classify_spatial_relationship(poly_a, poly_b)
        self.assertEqual(relationship, "OVERLAPPING")
        self.assertGreater(overlap_sqm, 0.0)
        print(f"[PASS] Unit Test 2: Known Polygons Test B — Overlap Intercepted ({overlap_sqm:.2f} sq.m)")

    def test_03_metric_area_reprojection(self):
        # Selaiyur plot in WGS84 reprojected to UTM EPSG:32644
        poly = Polygon([(80.1470, 12.9250), (80.1472, 12.9250), (80.1472, 12.9251), (80.1470, 12.9251), (80.1470, 12.9250)])
        area_sqm = calculate_metric_area_sqm(poly)
        self.assertGreater(area_sqm, 100.0)
        self.assertLess(area_sqm, 500.0)
        print(f"[PASS] Unit Test 3: Geodesic Metric Area Calculation ({area_sqm:.2f} sq.m)")


if __name__ == "__main__":
    unittest.main()
