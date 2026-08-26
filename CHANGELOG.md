# Changelog — PLOTPROOF Enterprise Evolution

All notable changes to the PlotProof platform are documented in this file.

## [Cycle 3] - 2026-08-26: Document Ingestion & Secure Storage Pipeline (Layer 3)

### Added
- **Multi-Vector Validation Engine**:
  - File extension verification (`.pdf`, `.jpg`, `.jpeg`, `.png`, `.tiff`).
  - Magic byte verification (`%PDF`, JPEG markers, PNG headers, TIFF endian flags).
  - 50 MB hard size limit enforcement with structured error responses (`FILE_TOO_LARGE`).
  - Malware & EICAR test string signature detection with ClamAV daemon probe and local heuristics (`MALWARE_DETECTED`).
- **Object Storage Service (`StorageService`)**:
  - S3 / MinIO integration using `boto3` with automatic fallback to secure local disk object storage.
  - Startup bucket initialization in `storage_init.py`.
  - Non-blocking socket probe to prevent connection hangs during local development.
  - Secure signed pre-signed download URLs expiring in 15 minutes (protecting documents from URL enumeration).
- **Relational Metadata & Job Queueing**:
  - SQLAlchemy `Document` model with `owner_user_id`, `storage_key`, `sha256`, `status`, `version`.
  - `ProcessingJob` model tracking OCR and downstream verification jobs (`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).
  - Immutable document versioning (`v1` -> `v2`) preventing title deed overwrites.
  - SHA-256 duplicate deed detection.
- **REST Endpoints (`/api/v1/documents`)**:
  - `POST /api/v1/documents` — Ingest, validate, fingerprint, store, queue OCR job.
  - `GET /api/v1/documents` — Role-aware listing (Citizens see own; Registrars/Admins see registry).
  - `GET /api/v1/documents/{id}` — Authenticated document metadata retrieval.
  - `GET /api/v1/documents/{id}/status` — Real-time processing and job lifecycle status.
  - `GET /api/v1/documents/{id}/download` — Short-lived signed download URL generator.
  - `DELETE /api/v1/documents/{id}` — Admin deletion with file cleanup and audit logging.
- **Database Migrations (Alembic)**:
  - Generated and executed migration `f8dc7b297149_add_document_storage_and_processing_jobs.py`.
- **Automated Testing Suite**:
  - Created `backend/tests/test_documents.py` with 12 comprehensive unit and security tests.

### Verified
- 12/12 tests in `backend/tests/test_documents.py` passing with 100% success.
- 12/12 tests in `backend/tests/test_auth.py` passing with 100% success.
- 3/3 tests in `backend/tests/test_pipeline.py` passing with 100% success (Total: 27/27 passing).
- Next.js production build (`npm run build`) compiles cleanly with 0 type errors across all 7 routes.

---



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
