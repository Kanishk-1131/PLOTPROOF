# Changelog — PLOTPROOF Enterprise Evolution

All notable changes to the PlotProof platform are documented in this file.

## [Cycle 5] - 2026-08-26: GIS & Spatial Validation Engine (Layer 5)

### Added
- **GIS Core Infrastructure (`app/gis/`)**:
  - `backend/app/gis/crs.py`: Geodesic coordinate projection from `EPSG:4326` (degrees) to `EPSG:32644` (UTM zone 44N metric projection for Tamil Nadu / South India) eliminating degree-squared distortion in statutory area calculations.
  - `backend/app/gis/geometry.py`: Enforces `(longitude=X, latitude=Y)` coordinate ordering, linear ring closing, geometry validation (`is_valid`, `is_empty`), and safe controlled repair (`make_valid` / safe `buffer(0)` with <= 5% area drift preservation).
  - `backend/app/gis/overlap.py`: Topological relationship classifier (`DISJOINT`, `TOUCHING`, `OVERLAPPING`, `WITHIN`, `CONTAINS`, `IDENTICAL`), boundary touch tolerance (`TOUCH_TOLERANCE_METERS = 0.05`), exact intersection area calculation, overlap percentage, and area consistency calculation (`<= 1% NORMAL`, `1-5% REVIEW`, `> 5% HIGH_RISK`).
  - `backend/app/gis/risk.py`: Multi-factor spatial risk scoring engine (Geometry 20%, Overlap 35%, Area Mismatch 20%, Coordinate Confidence 10%, Parcel ID 15%) producing explicit 0-100 scores and risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Relational Models & Database Migrations**:
  - `backend/app/models/parcel.py`: SQLAlchemy `Parcel` model with database-agnostic `CompatibleGeometry` (PostGIS `Geometry(POLYGON, 4326)` on PostgreSQL and WKT text on SQLite).
  - `backend/app/models/spatial_validation.py`: `SpatialValidation` model recording geometry validity, overlap detection, intersection area, area difference, risk score, and reproducible audit metadata (`algorithm_version`, `dataset_version`, `crs`, timestamp, result).
  - Generated and executed Alembic migration `0406b1ae86d4_add_gis_parcel_and_spatial_validation_.py`.
- **REST Endpoints (`/api/v1`)**:
  - `POST /api/v1/documents/{id}/spatial/validate`: Full spatial validation execution returning Layer 5 Handshake Contract Payload.
  - `GET /api/v1/documents/{id}/spatial`: Spatial validation results, relationship, and risk score.
  - `GET /api/v1/documents/{id}/spatial/map`: Privacy-isolated GeoJSON FeatureCollection containing strictly candidate and reference parcels.
  - `GET /api/v1/parcels/{id}`: Reference cadastral parcel inspection.
- **Automated Testing Suite**:
  - Created `backend/tests/test_gis.py` covering 12 comprehensive unit and spatial tests (Coordinate ordering, repair, metric projection, touch vs overlap, exact overlap calculation, area tiers, risk factors, Case C text-only geometry insufficient flag, clean deed validation, spatial collision detection, privacy GeoJSON map, and reference dataset read-only invariance).

### Verified
- 12/12 tests in `backend/tests/test_gis.py` passing with 100% success.
- Total 51/51 tests passing across all layers (`test_auth.py`, `test_pipeline.py`, `test_documents.py`, `test_ocr.py`, `test_gis.py`).
- Next.js production build (`npm run build`) compiles cleanly with 0 type errors across all 7 routes.

---



### Added
- **OCR Engine Infrastructure**:
  - `backend/app/ocr/preprocess.py`: Multi-variant image preprocessing pipeline (Original, Grayscale, Denoised with `fastNlMeansDenoising`, Adaptive Gaussian Thresholding, and CLAHE contrast enhancement) + automatic deskew orientation correction.
  - `backend/app/ocr/engines.py`: Dual-engine architecture with `PyMuPDF` vector/layout text parsing and Tesseract engine fallback.
  - `backend/app/ocr/normalize.py`: Deterministic normalizers for Survey Numbers (`142 / 3A` -> `142/3A`), area unit standardizer to Square Meters (Acres, Cents, Ground, Gunthas, Sq.ft), boundary trimmer, and coordinate parser with geographic bounding box validation.
  - `backend/app/ocr/extract.py`: `FieldExtractionEngine` extracting deed registration numbers, deed dates, survey numbers, subdivisions, districts, taluks, villages, areas, 4 boundaries, and GPS coordinates.
  - `backend/app/ocr/confidence.py`: Field-level confidence tier classifier (`HIGH` >= 0.90, `MEDIUM` 0.70-0.89, `LOW` < 0.70) and automatic `Human Review` trigger flag.
- **Relational Models & Database Migrations**:
  - `backend/app/models/ocr_result.py`: SQLAlchemy `OCRResult` storing full document text, word-level bounding boxes (`bbox`), engine name, and timestamp.
  - `backend/app/models/ocr_field.py`: SQLAlchemy `OCRField` storing extracted key-value pairs, field-level confidence, status (`EXTRACTED`, `CONFIRMED`, `CORRECTED`, `REJECTED`), and source text.
  - Generated and applied Alembic migration `13745b9b6e54_add_ocr_extraction_tables.py`.
- **API Endpoints (`/api/v1/documents`)**:
  - `GET /api/v1/documents/{id}/ocr`: Full raw OCR text and bounding boxes for spatial inspection.
  - `GET /api/v1/documents/{id}/fields`: Structured land title fields with confidence scoring.
  - `PATCH /api/v1/documents/{id}/fields/{field_id}`: Statutory human correction workflow (restricted to Sub-Registrars/Admins with audit logging).
  - `POST /api/v1/documents/{id}/ocr/reprocess`: On-demand re-extraction endpoint returning Layer 5 Handshake Contract Payload.
- **Automated Testing Suite**:
  - Created `backend/tests/test_ocr.py` covering 12 comprehensive test scenarios (Clean deed, preprocessing variants, deskew orientation, Tamil regional normalizers, multi-unit conversions, coordinate bounds, missing survey review trigger, REST endpoints, Sub-Registrar corrections, Citizen 403 authorization, Layer 5 contract schema, and reprocessing).

### Verified
- 12/12 tests in `backend/tests/test_ocr.py` passing with 100% success.
- Total 39/39 tests passing across all layers (`test_auth.py`, `test_pipeline.py`, `test_documents.py`, `test_ocr.py`).
- Next.js production build (`npm run build`) compiles cleanly with 0 type errors across all 7 routes.

---



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
