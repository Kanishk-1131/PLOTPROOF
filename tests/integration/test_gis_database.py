import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.parcel import Parcel
from app.services.gis_service import GISService


class TestIntegrationGISDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls.gis_service = GISService()

    def test_01_cadastral_parcels_seeded_and_queried(self):
        db = SessionLocal()
        try:
            parcels = db.query(Parcel).all()
            self.assertGreaterEqual(len(parcels), 3)
            # Find Survey 142/3A
            p_142 = db.query(Parcel).filter(Parcel.survey_number == "142/3A").first()
            self.assertIsNotNone(p_142)
            self.assertEqual(p_142.village, "Selaiyur")
            self.assertGreater(p_142.area_sq_m, 100.0)
            self.assertIsNotNone(p_142.to_shapely())
            print("[PASS] Integration Test 1: Authoritative Cadastral Reference Dataset Queried from Database")

        finally:
            db.close()

    def test_02_cadastral_layer_read_only_invariance(self):
        db = SessionLocal()
        try:
            count_before = db.query(Parcel).count()
            # Perform spatial validations
            self.gis_service.get_cadastral_layer(db)
            count_after = db.query(Parcel).count()
            self.assertEqual(count_before, count_after)
            print("[PASS] Integration Test 2: Cadastral Reference Dataset Read-Only Invariance Verified")
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
