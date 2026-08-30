import sys
import unittest
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.blockchain.service import to_bytes32_hex



class TestUnitBlockchain(unittest.TestCase):
    """
    Layer 12: Unit tests for Blockchain Digest Encoding & Contract ABI Interop.
    """

    def test_01_to_bytes32_hex_length_and_prefix(self):
        val = "PP-2026-000052"
        b32 = to_bytes32_hex(val)
        self.assertTrue(b32.startswith("0x"))
        self.assertEqual(len(b32), 66)  # 0x + 64 hex chars = 32 bytes
        print("[PASS] Unit Test 1: Fixed-Size bytes32 Hex Normalization Verified")

    def test_02_to_bytes32_hex_reproducibility(self):
        val = "0x" + "c" * 64
        b32_1 = to_bytes32_hex(val)
        b32_2 = to_bytes32_hex(val)
        self.assertEqual(b32_1, b32_2)
        self.assertEqual(b32_1, val)
        print("[PASS] Unit Test 2: Hex String Invariance in bytes32 Encoding")

    def test_03_zero_pii_in_bytes32_parameters(self):
        sensitive_name = "Rajesh Kumar 1234-5678-9012"
        b32 = to_bytes32_hex(sensitive_name)
        # Should only contain hex digest, not plain string
        self.assertNotIn("Rajesh", b32)
        self.assertNotIn("1234", b32)
        print("[PASS] Unit Test 3: Cryptographic Digest Sanitization of Sensitive Inputs")


if __name__ == "__main__":
    unittest.main()
