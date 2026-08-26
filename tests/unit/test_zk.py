import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.privacy.commitments import (
    compute_poseidon_commitment,
    generate_commitment_secret,
    create_deed_commitment,
    BN254_PRIME,
)


class TestUnitZK(unittest.TestCase):
    """
    Layer 12: Unit tests for Zero-Knowledge Circuits & Algebraic Commitments.
    """

    def test_01_poseidon_determinism_and_field_order(self):
        h1 = compute_poseidon_commitment("12345", "67890")
        h2 = compute_poseidon_commitment("12345", "67890")
        self.assertEqual(h1, h2)
        int_val = int(h1)
        self.assertLess(int_val, BN254_PRIME)
        print("[PASS] Unit Test 1: Poseidon Hash Determinism & BN254 Prime Field Bounding")

    def test_02_commitment_non_collision_with_different_secrets(self):
        doc_hash = "a" * 64
        verif_hash = "b" * 64
        s1 = generate_commitment_secret()
        s2 = generate_commitment_secret()

        _, c1 = create_deed_commitment(doc_hash, verif_hash, s1)
        _, c2 = create_deed_commitment(doc_hash, verif_hash, s2)
        self.assertNotEqual(c1, c2)
        print("[PASS] Unit Test 2: Commitment Non-Collision with Distinct Secrets")

    def test_03_commitment_invalidated_by_hash_modification(self):
        s = generate_commitment_secret()
        _, c_orig = create_deed_commitment("a" * 64, "b" * 64, s)
        _, c_alt = create_deed_commitment("f" * 64, "b" * 64, s)
        self.assertNotEqual(c_orig, c_alt)
        print("[PASS] Unit Test 3: Altered Document Hash Invalidation of Public Commitment")


if __name__ == "__main__":
    unittest.main()
