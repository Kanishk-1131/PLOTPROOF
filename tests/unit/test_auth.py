import sys
import unittest
from pathlib import Path
from datetime import timedelta

backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    decode_access_token,
)
from app.models.user import UserRole


class TestUnitAuth(unittest.TestCase):
    """
    Layer 12: Unit tests for Authentication & Cryptographic Hashing primitives.
    """

    def test_01_argon2id_password_hashing(self):
        plain_pwd = "SuperSecretPassword123!"
        hashed = hash_password(plain_pwd)
        self.assertNotEqual(plain_pwd, hashed)
        self.assertTrue(verify_password(plain_pwd, hashed))
        self.assertFalse(verify_password("WrongPassword123!", hashed))
        print("[PASS] Unit Test 1: Argon2id Password Hashing & Verification")


    def test_02_jwt_token_generation_and_decoding(self):
        user_id = 42
        role = UserRole.CITIZEN.value
        token = create_access_token(user_id=user_id, role=role, expires_delta=timedelta(minutes=15))
        payload = decode_access_token(token)
        self.assertIsNotNone(payload)
        self.assertEqual(int(payload.get("sub")), user_id)
        self.assertEqual(payload.get("role"), role)
        print("[PASS] Unit Test 2: JWT Minimal Claims Packaging & Decoding")

    def test_03_jwt_tampered_signature_rejection(self):
        token = create_access_token(user_id=1, role="CITIZEN")
        parts = token.split(".")
        # Tamper payload
        tampered_token = f"{parts[0]}.eyJuZXdfcm9sZSI6ICJBRE1JTiJ9.{parts[2]}"
        payload = decode_access_token(tampered_token)
        self.assertIsNone(payload)
        print("[PASS] Unit Test 3: Tampered JWT Signature Rejection")

    def test_04_jwt_expired_token_rejection(self):
        expired_token = create_access_token(user_id=1, role="CITIZEN", expires_delta=timedelta(seconds=-10))
        payload = decode_access_token(expired_token)
        self.assertIsNone(payload)
        print("[PASS] Unit Test 4: Expired JWT Token Rejection")


if __name__ == "__main__":
    unittest.main()
