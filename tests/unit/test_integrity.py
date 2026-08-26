import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.integrity.hashing import sha256_bytes
from app.integrity.canonical import canonical_json
from app.integrity.fingerprint import create_verification_hash


class TestUnitIntegrity(unittest.TestCase):
    """
    Layer 12: Unit tests for Cryptographic Fingerprinting & RFC 8785 Canonical Serialization.
    """

    def test_01_single_byte_hash_flipping(self):
        doc_a = b"%PDF-1.4 Original Deed Document"
        doc_b = b"%PDF-1.4 1riginal Deed Document"  # Single bit/byte flip
        hash_a = sha256_bytes(doc_a)
        hash_b = sha256_bytes(doc_b)
        self.assertNotEqual(hash_a, hash_b)
        print("[PASS] Unit Test 1: Single Byte Alteration Interception via SHA-256")

    def test_02_canonical_json_key_order_invariance(self):
        dict_1 = {"survey_number": "142/3A", "area_sqm": 222.97, "district": "Chennai"}
        dict_2 = {"district": "Chennai", "area_sqm": 222.97, "survey_number": "142/3A"}
        json_1 = canonical_json(dict_1)
        json_2 = canonical_json(dict_2)
        self.assertEqual(json_1, json_2)
        self.assertEqual(sha256_bytes(json_1), sha256_bytes(json_2))
        print("[PASS] Unit Test 2: RFC 8785 Canonical JSON Deterministic Key Sorting")

    def test_03_verification_chain_dependency(self):
        file_h = sha256_bytes(b"document_file")
        ocr_h = sha256_bytes(b"ocr_data")
        meta_h = sha256_bytes(b"metadata")
        spatial_a = sha256_bytes(b"spatial_clean")
        spatial_b = sha256_bytes(b"spatial_collision")

        chain_a = create_verification_hash(file_h, ocr_h, meta_h, spatial_a)
        chain_b = create_verification_hash(file_h, ocr_h, meta_h, spatial_b)
        self.assertNotEqual(chain_a, chain_b)
        print("[PASS] Unit Test 3: Verification Hash Chain Stage Interdependency")


if __name__ == "__main__":
    unittest.main()
