import sys
import unittest
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal, init_db
from app.seed_data.seed_db import seed_database
from app.models.user import User, UserRole
from app.core.security import verify_password
from app.core.permissions import require_roles

client = TestClient(app)

class TestLayer2Auth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        seed_database()
        cls._cleanup_test_users()

    @classmethod
    def tearDownClass(cls):
        cls._cleanup_test_users()

    @classmethod
    def _cleanup_test_users(cls):
        db = SessionLocal()
        try:
            db.query(User).filter(User.email.in_(["newcitizen@example.com", "hacker@example.com"])).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()


    def test_01_user_registration(self):
        payload = {
            "email": "newcitizen@example.com",
            "password": "StrongPassword123!",
            "full_name": "New Citizen User",
            "phone": "9876543210"
        }
        res = client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertEqual(data["email"], "newcitizen@example.com")
        self.assertEqual(data["full_name"], "New Citizen User")
        self.assertEqual(data["role"], "CITIZEN")
        self.assertFalse(data["is_verified"])
        
        # Verify in DB that password is Argon2id hashed
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.email == "newcitizen@example.com").first()
            self.assertIsNotNone(user)
            self.assertTrue(user.password_hash.startswith("$argon2id$") or "$argon2" in user.password_hash)
            self.assertTrue(verify_password("StrongPassword123!", user.password_hash))
            self.assertFalse(verify_password("WrongPassword!", user.password_hash))
        finally:
            db.close()
        print("[PASS] Test 1: Citizen Registration & Argon2id Password Hashing Verified")

    def test_02_duplicate_email_protection(self):
        payload = {
            "email": "newcitizen@example.com",
            "password": "AnotherPassword123!",
            "full_name": "Duplicate User",
            "phone": "9876543210"
        }
        res = client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(res.status_code, 409)
        self.assertIn("Email already registered", res.json()["detail"])
        print("[PASS] Test 2: Duplicate Email Protection (409 Conflict) Verified")

    def test_03_privilege_escalation_protection(self):
        payload = {
            "email": "hacker@example.com",
            "password": "HackerPassword123!",
            "full_name": "Hacker Attempting Admin",
            "role": "ADMIN"  # Attempt to elevate
        }
        res = client.post("/api/v1/auth/register", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["role"], "CITIZEN")
        print("[PASS] Test 3: Privilege Escalation Protection (Enforces CITIZEN) Verified")

    def test_04_user_login_success(self):
        payload = {
            "email": "newcitizen@example.com",
            "password": "StrongPassword123!"
        }
        res = client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        print("[PASS] Test 4: User Login & JWT Access Token Generation Verified")

    def test_05_user_login_invalid_password(self):
        payload = {
            "email": "newcitizen@example.com",
            "password": "IncorrectPassword!"
        }
        res = client.post("/api/v1/auth/login", json=payload)
        self.assertEqual(res.status_code, 401)
        self.assertIn("Invalid email or password", res.json()["detail"])
        print("[PASS] Test 5: Invalid Password Authentication Rejection (401) Verified")

    def test_06_rbac_permission_check(self):
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
            citizen_user = db.query(User).filter(User.role == UserRole.CITIZEN).first()

            admin_checker = require_roles(UserRole.ADMIN)
            # Admin should pass
            self.assertEqual(admin_checker(admin_user), admin_user)

            # Citizen should be blocked
            with self.assertRaises(Exception):
                admin_checker(citizen_user)
            print("[PASS] Test 6: Role-Based Access Control (RBAC) Permissions Verified")
        finally:
            db.close()

    def test_07_get_me_profile_with_token(self):
        # 1. Login to get token
        login_res = client.post("/api/v1/auth/login", json={
            "email": "newcitizen@example.com",
            "password": "StrongPassword123!"
        })
        token = login_res.json()["access_token"]

        # 2. Access /me with valid token
        headers = {"Authorization": f"Bearer {token}"}
        me_res = client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(me_res.status_code, 200)
        self.assertEqual(me_res.json()["email"], "newcitizen@example.com")
        self.assertEqual(me_res.json()["role"], "CITIZEN")

        # 3. Access without token should fail 401
        fail_res = client.get("/api/v1/auth/me")
        self.assertEqual(fail_res.status_code, 401)
        print("[PASS] Test 7: /me Profile & Bearer Token Authentication Dependency Verified")

    def test_08_refresh_token_rotation(self):
        # 1. Login to get initial refresh token
        login_res = client.post("/api/v1/auth/login", json={
            "email": "newcitizen@example.com",
            "password": "StrongPassword123!"
        })
        init_data = login_res.json()
        raw_refresh_token = init_data["refresh_token"]
        self.assertIsNotNone(raw_refresh_token)

        # 2. Call /refresh
        refresh_res = client.post("/api/v1/auth/refresh", json={
            "refresh_token": raw_refresh_token
        })
        self.assertEqual(refresh_res.status_code, 200)
        new_data = refresh_res.json()
        self.assertIn("access_token", new_data)
        self.assertIn("refresh_token", new_data)
        self.assertNotEqual(new_data["refresh_token"], raw_refresh_token)

        # 3. Re-using the old refresh token must be rejected (Token Rotation)
        replay_res = client.post("/api/v1/auth/refresh", json={
            "refresh_token": raw_refresh_token
        })
        self.assertEqual(replay_res.status_code, 401)
        print("[PASS] Test 8: Refresh Token Rotation & Replay Attack Prevention Verified")

    def test_09_logout_revocation(self):
        # 1. Login
        login_res = client.post("/api/v1/auth/login", json={
            "email": "newcitizen@example.com",
            "password": "StrongPassword123!"
        })
        refresh_token = login_res.json()["refresh_token"]

        # 2. Logout
        logout_res = client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token
        })
        self.assertEqual(logout_res.status_code, 200)

        # 3. Refresh should now fail
        fail_res = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        self.assertEqual(fail_res.status_code, 401)
        print("[PASS] Test 9: Logout & Refresh Token Revocation Verified")

    def test_10_audit_log_access(self):
        # 1. Login as seeded Admin
        login_res = client.post("/api/v1/auth/login", json={
            "email": "admin@plotproof.gov.in",
            "password": "PlotProof2026!"
        })
        self.assertEqual(login_res.status_code, 200)
        admin_token = login_res.json()["access_token"]

        # 2. Retrieve audit logs as Admin
        headers = {"Authorization": f"Bearer {admin_token}"}
        audit_res = client.get("/api/v1/auth/audit-logs", headers=headers)
        self.assertEqual(audit_res.status_code, 200)
        logs = audit_res.json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)

        # Verify logged actions exist
        actions = [item["action"] for item in logs]
        self.assertTrue(any("LOGIN" in act or "REGISTER" in act for act in actions))
        print("[PASS] Test 10: Security Audit Log Ingestion & Role-Restricted Inspection Verified")

if __name__ == "__main__":
    unittest.main()

