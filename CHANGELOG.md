# Changelog — PLOTPROOF Enterprise Evolution

All notable changes to the PlotProof platform are documented in this file.

## [Cycle 10] - 2026-08-26: Production Security, Authentication & Deployment (Layer 10)

### Added
- **Production Security Middleware (`backend/app/middleware/security.py`)**:
  - `SecurityHeadersMiddleware`: Injects Content Security Policy (`CSP`), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, and HTTP Strict Transport Security (`HSTS`).
  - `RequestIDMiddleware`: End-to-end traceable `X-Request-ID` and latency telemetry (`X-Response-Time-Ms`).
  - `InMemoryRateLimiter`: Adaptive sliding-window rate limiter differentiating standard operations from CPU-heavy operations (OCR extraction, ZK Groth16 proving).
- **Secure File Validation & Boundary Enforcement**:
  - Magic bytes and MIME signature verification blocking disguised executables and shell scripts.
  - Path traversal protection (`../../`) with filename sanitization and object-storage quarantine.
  - Hard file size limit (50MB) preventing upload-based denial of service.
- **Enterprise Infrastructure & Disaster Recovery**:
  - `infrastructure/nginx/nginx.conf`: Production Nginx reverse proxy with rate limiting zones, upload body sizing, TLS, and static proxy caching.
  - `infrastructure/scripts/backup.sh`: PostgreSQL/PostGIS dump and encrypted object storage snapshot script with automated 30-day retention policies.
  - `.github/workflows/ci.yml`: Full GitHub Actions CI/CD matrix executing linting, multi-layer backend tests, contract tests, and Next.js production builds.
- **System Health Probes**:
  - `GET /health`: Fast liveness probe.
  - `GET /ready`: Comprehensive readiness probe verifying PostgreSQL/SQLite and storage availability.
- **Automated Security & RBAC Test Suite**:
  - `backend/tests/test_security.py` (12 tests) verifying IDOR cross-tenant isolation, RBAC privilege enforcement, security headers, magic bytes, path traversal sanitization, rate limiting, and minimal JWT claims.

---

## [Cycle 9] - 2026-08-26: Certificate Generation & Public Verification Portal (Layer 9)

### Added
- **Tamper-Evident Verification Certificate Generator (`backend/app/certificate/`)**:
  - `backend/app/certificate/generator.py`: Generates professional, publication-ready PDF certificate via ReportLab.
  - Generates distinct human-readable Certificate Number (`PP-CERT-2026-000052`) separate from Verification ID (`PP-2026-000052`).
  - Computes SHA-256 byte digest (`certificate_hash`) stored in database for byte-level tamper verification.
  - Strictly enforces statutory legal disclaimer:
    *"PlotProof System Verification Certificate. This certificate confirms the verification results produced by the PlotProof system. It does not independently constitute a government-issued title document or legal title guarantee."*
- **Public Verification QR Generator (`backend/app/certificate/qr.py`)**:
  - Produces crisp, pure public verification URL QR codes (`https://plotproof.gov.in/verify/{verification_id}`) strictly omitting citizen PII, raw deeds, and private keys.
- **Certificate Revocation & Audit Machine**:
  - Revocation workflow (`POST /api/v1/certificates/{id}/revoke`) restricted strictly to Registrar and Admin roles.
  - Invalidates active certificates to `REVOKED` state with reason, actor, and timestamp.
  - Public portal dynamically displays `! CERTIFICATE REVOKED` banner.
- **Relational Models & Database Migrations**:
  - `backend/app/models/certificate.py`: `Certificate` storing `document_id`, `verification_id`, `certificate_number`, `certificate_hash`, `file_path`, `status`, `revoked_at`, `revocation_reason`, and `revoked_by`.
  - Applied Alembic migration `76e46ab2965f_add_certificates_table.py`.
- **Public Verification Portal Frontend**:
  - `frontend/app/verify/[verificationId]/page.tsx`: Modern Next.js verification page handling `VERIFIED`, `REVOKED`, `BLOCKCHAIN_PENDING`, `REVIEW_REQUIRED`, and `SPATIAL_RISK`.
- **Automated Testing Suite**:
  - `backend/tests/test_certificate.py` (12 tests) verifying PDF generation, prerequisite gating, QR encoding, download access control, SHA-256 tamper verification, revocation, and zero-PII public exposure.

---

## [Cycle 8] - 2026-08-26: Blockchain & Smart Contract Anchoring (Layer 8)


### Added
- **Smart Contract Architecture (`blockchain/contracts/PlotProofRegistry.sol`)**:
  - OpenZeppelin `Ownable` contract storing compact, fixed-size `bytes32` cryptographic digests (`verificationId`, `verificationHash`, `commitment`, `timestamp`).
  - Emits `VerificationAnchored(bytes32 indexed verificationId, bytes32 indexed verificationHash, bytes32 indexed commitment, uint64 timestamp)`.
  - Zero citizen PII, zero raw deeds, and zero ZK witnesses on-chain.
  - Multi-tier duplicate protection at smart contract, database, and backend service levels.
- **Hardhat Infrastructure & Smart Contract Tests**:
  - `blockchain/hardhat.config.js`: Supports Hardhat local network (Chain ID 31337) and Polygon Amoy testnet.
  - `blockchain/scripts/deploy.js`: Deterministic deployment script.
  - `blockchain/test/PlotProofRegistry.test.js`: 6 unit tests verifying successful anchor, duplicate rejection, owner access control, bytes32 retrieval, and input validation.
- **Backend Blockchain Engine (`app/blockchain/`)**:
  - `backend/app/blockchain/service.py`: `BlockchainService` orchestrating prerequisite validation (Integrity PASS, GIS PASS, ZK proof VALID), transaction generation, mining confirmation, and tamper cross-checking.
  - Cross-checks database records against on-chain anchor: intercepts database tampering (`BLOCKCHAIN_ANCHOR_MISMATCH`) if database hash is compromised.
- **Relational Models & Database Migrations**:
  - `backend/app/models/blockchain_anchor.py`: `BlockchainAnchor` storing `verification_id`, `transaction_hash`, `block_number`, `contract_address`, `network`, and `status`.
  - Applied Alembic migration `48f0283dcbbc_add_zk_proof_and_blockchain_anchor_.py`.
- **REST Endpoints (`/api/v1`)**:
  - `POST /api/v1/documents/{id}/blockchain/anchor`: Anchors verified document on Polygon.
  - `GET /api/v1/documents/{id}/blockchain`: Retrieves blockchain transaction receipt.
  - `GET /api/v1/verification/{verification_id}`: Public verification endpoint cross-checking database against on-chain state.
- **Automated Testing Suite**:
  - Created `backend/tests/test_blockchain.py` (12 tests) passing with 100% success.

---

## [Cycle 7] - 2026-08-26: Privacy & Zero-Knowledge Proof System (Layer 7)

### Added
- **Circom Circuit & Groth16 Infrastructure (`blockchain/zk/`)**:
  - `blockchain/zk/circuits/land_verification.circom`: Non-linear algebraic binding proving `Poseidon(privateRecord, secret) == publicCommitment` and `validationStatus == 1` without revealing private identity or deed data.
  - `blockchain/zk/build/verification_key.json`: BN254 Groth16 verification key parameters (`land-verification-v1`, `vk-v1`).
  - `blockchain/zk/scripts/generate-proof.js` & `verify-proof.js`: Standalone Node.js CLI proof generator and verifier.
- **Backend Privacy & Commitment Engine (`app/privacy/`)**:
  - `backend/app/privacy/commitments.py`: Deterministic algebraic Poseidon commitment calculator bounded in BN254 scalar field order.
  - `backend/app/privacy/privacy_policy.py`: Strict PII minimization scrubbing Aadhaar, PAN, phone, owner names, addresses, and secrets from all public signals and responses.
  - `backend/app/privacy/zk_service.py`: `ZKService` enforcing prerequisite checks (Integrity PASS, GIS PASS, Status APPROVED), witness isolation (never persisted or returned to API), Groth16 proof generation, and local verification before declaring valid.
- **Relational Models & Database Migrations**:
  - `backend/app/models/zk_proof.py`: `ZKProofRecord` storing `proof_id`, `commitment`, `public_signals`, `proof_json`, `circuit_version`, and `verification_key_version`.
- **REST Endpoints (`/api/v1`)**:
  - `POST /api/v1/documents/{id}/privacy/commit`: Generates Poseidon commitment with cryptographic salt.
  - `POST /api/v1/documents/{id}/privacy/prove`: Generates and locally verifies Groth16 ZK proof.
  - `POST /api/v1/documents/{id}/privacy/verify`: Locally verifies proof against verification key and public signals.
  - `GET /api/v1/documents/{id}/privacy/status`: Privacy dashboard status (`private_identity: PROTECTED`, `sensitive_data_exposed: NO`).
- **Standardized Handshake for Layer 8**:
  - Produces `ZKBlockchainHandshakePayload` linking verification hash, commitment, proof, and signals.
- **Automated Testing Suite**:
  - Created `backend/tests/test_privacy.py` (12 tests) passing with 100% success.

---

## [Cycle 6] - 2026-08-26: Integrity, Fraud Detection & Cryptographic Verification (Layer 6)


### Added
- **Cryptographic Hash Chain & Canonical Serialization (`app/integrity/`)**:
  - `backend/app/integrity/hashing.py`: High-performance deterministic SHA-256 byte and chunked file stream hashers.
  - `backend/app/integrity/canonical.py`: Canonical JSON serializer enforcing RFC 8785 lexicographical key sorting, compact `(',', ':')` delimiters, and UTF-8 encoding.
  - `backend/app/integrity/fingerprint.py`: Deterministic stage fingerprinting for structured metadata (`metadata_hash`), OCR text/bounding blocks (`ocr_hash`), and Layer 5 spatial results (`spatial_hash`).
  - Implemented `create_verification_hash` assembling the composite cryptographic chain: `File Hash + OCR Hash + Metadata Hash + Spatial Hash -> Verification Hash`.
  - `backend/app/integrity/verification.py`: Multi-state verification lifecycle state machine (`PROCESSING`, `INTEGRITY_CHECKED`, `GIS_VALIDATED`, `REVIEW_REQUIRED`, `APPROVED`, `ANCHORED`) with distinct anomaly classifiers (Cryptographic Tampering `INTEGRITY_FAILURE`, Spatial Collision `SPATIAL_RISK`, and Low-Confidence OCR `REVIEW_REQUIRED`), avoiding generic fraud conflation.
- **Relational Models & Database Migrations**:
  - `backend/app/models/integrity_record.py`: SQLAlchemy `IntegrityRecord` storing per-stage hashes (`file_hash`, `ocr_hash`, `metadata_hash`, `spatial_hash`, `verification_hash`).
  - `backend/app/models/audit_event.py`: SQLAlchemy `AuditEvent` capturing immutable timeline actions (`DOCUMENT_UPLOADED`, `OCR_COMPLETED`, `FIELD_CORRECTED`, `GIS_VALIDATED`, `INTEGRITY_CREATED`, `INTEGRITY_VERIFIED`).
  - Applied Alembic migration `def583e5add1_add_integrity_and_audit_tables.py`.
- **Statutory Correction & Version Invalidation Workflow**:
  - Connected Sub-Registrar field corrections to `IntegrityService.invalidate_on_field_correction`: bumps document version (`v1 -> v2`), resets spatial validation status to `REVALIDATION_REQUIRED`, recomputes composite hashes, and writes an audit event.
- **REST Endpoints (`/api/v1`)**:
  - `POST /api/v1/documents/{id}/integrity/generate`: Generates/updates the multi-stage cryptographic integrity chain.
  - `GET /api/v1/documents/{id}/integrity`: Retrieves the integrity record and verification status.
  - `POST /api/v1/documents/{id}/integrity/verify`: Verifies byte-for-byte fidelity of presented files (detects single-byte tampering).
  - `GET /api/v1/verify/public/{verification_id}`: Public QR verification endpoint for banks/lawyers strictly omitting citizen PII (no Aadhaar, phone number, owner name, or raw deed).
- **Automated Testing Suite**:
  - Created `backend/tests/test_integrity.py` with 12 tests covering all verification scenarios.

### Verified
- 12/12 tests in `backend/tests/test_integrity.py` passing with 100% success.
- Total 63/63 tests passing across all 6 layers (`test_auth.py`, `test_pipeline.py`, `test_documents.py`, `test_ocr.py`, `test_gis.py`, `test_integrity.py`).
- Next.js production build (`npm run build`) compiles cleanly with 0 type errors across all 7 routes.

---

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
