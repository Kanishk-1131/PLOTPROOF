# Changelog — PLOTPROOF Enterprise Evolution

All notable changes to the PlotProof platform are documented in this file.

## [Cycle 2] - 2026-08-26: Identity, Authentication & Access Control (Layer 2 Hardening)

### Added
- **Argon2id Password Security**: Integrated `pwdlib` Argon2id hashing with secure salting for all user credentials.
- **Refresh Token Rotation & Revocation**: Added `refresh_tokens` model, cryptographic SHA-256 token hashing, single-use rotation, and replay prevention.
- **Audit Logging System**: Added `audit_logs` tracking registration, logins, token rotation, and security events.
- **FastAPI Authentication Dependencies**: Added `get_current_user` Bearer token extraction and validation.
- **Endpoints**:
  - `POST /api/v1/auth/refresh` — token rotation.
  - `POST /api/v1/auth/logout` — session revocation.
  - `GET /api/v1/auth/me` — authenticated user profile.
  - `GET /api/v1/auth/audit-logs` — role-protected audit inspection for Admins and Registrars.
- **Alembic Database Migrations**: Initialized Alembic migration environment and generated initial schema migration `6b9d6b2d7b6c`.
- **Frontend Role-Based Authentication**:
  - Created `AuthContext.tsx` with JWT persistence and automatic Axios `Authorization` header injection.
  - Created `AuthModal.tsx` supporting 1-click Quick Demo Role Switcher across Citizen, Sub-Registrar, Bank Officer, and System Admin personas.
  - Integrated dynamic role badge and persona switcher into `Navbar.tsx`.
- **Antigravity Customization Architecture**:
  - Created `.agents/` hierarchy with global and project rules, skills (`hackathon-builder`, `ui-ux-reviewer`, `debugging`), subagent (`hackathon-judge`), and 6 workflow slash commands.
  - Added structured documentation under `docs/` (`PRD.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `API.md`).

### Changed
- Unified database connection pooling across `session.py` and `connection.py` to eliminate connection drift and ensure SQLite/Postgres compatibility.
- Upgraded `JWT_SECRET` to a high-entropy 64-byte key eliminating HMAC length deprecation warnings.
- Made auth unit tests idempotent with automatic cleanup in `test_auth.py`.

### Verified
- 10/10 tests in `backend/tests/test_auth.py` passing with 100% success.
- 3/3 tests in `backend/tests/test_pipeline.py` passing with 100% success.
- Next.js frontend production build (`npm run build`) compiles cleanly with 0 type errors.

---

## [Cycle 1] - 2026-08-26: Core Forensic Verification Pipeline (Layer 1)
- Initialized FastAPI multi-vector verification engine.
- Implemented OpenCV image preprocessing and OCR field extraction.
- Implemented Shapely/GeoPandas cadastral spatial boundary collision detection.
- Anchored deterministic SHA-256 document fingerprints with smart contract interfaces.
- Built Next.js UI with interactive Leaflet GIS map, 6-stage verification stepper, and QR code certificate generator.
