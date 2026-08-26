# PlotProof REST API Reference

The interactive OpenAPI specification is available live at `http://localhost:8000/docs`.

---

## 1. Authentication (`/api/v1/auth`)

### `POST /api/v1/auth/register`
Registers a new user account.
- **Request:** `{"email": "...", "password": "...", "full_name": "...", "phone": "..."}`
- **Response:** `200 OK` `UserResponse`

### `POST /api/v1/auth/login`
Authenticates credentials and issues JWT access token + refresh token.
- **Request:** `{"email": "...", "password": "..."}`
- **Response:** `200 OK` `{"access_token": "...", "token_type": "bearer", "refresh_token": "...", "user": {...}}`

### `GET /api/v1/auth/me`
Returns profile and role claims of currently authenticated user.
- **Headers:** `Authorization: Bearer <token>`
- **Response:** `200 OK` `UserResponse`

---

## 2. Document Ingestion (`/api/v1/documents`)

### `POST /api/v1/documents`
Secure multipart deed upload with magic-bytes sniffing and malware scanning.
- **Headers:** `Authorization: Bearer <token>`
- **Form Data:** `file: <binary PDF/TIFF>`
- **Response:** `201 Created` `{"document_id": 1, "file_name": "deed.pdf", "sha256": "...", "status": "QUEUED", "version": 1}`

### `GET /api/v1/documents/{id}`
Returns document status, metadata, and processing queue position.

### `GET /api/v1/documents/{id}/download`
Generates an access-controlled, temporary signed URL to download deed file.

---

## 3. Orchestration & State Machine (`/api/v1/verifications`)

### `POST /api/v1/verifications`
Triggers full end-to-end verification pipeline across OCR, GIS, Integrity, ZK, Blockchain, and Certificate stages.
- **Headers:** `Authorization: Bearer <token>`
- **Request:** `{"document_id": 1}`
- **Response:** `200 OK` `VerificationStatusResponse`

### `GET /api/v1/verifications/{verification_id}`
Returns live stage-by-stage progression telemetry.

### `POST /api/v1/verifications/{verification_id}/retry`
Resumes stalled or failed verifications from last successful checkpoint without repeating expensive OCR/GIS stages.

### `POST /api/v1/verifications/{verification_id}/review`
Sub-Registrar statutory decision endpoint for spatial boundary variances.
- **Headers:** `Authorization: Bearer <registrar_token>`
- **Request:** `{"decision": "APPROVED" | "REJECTED", "remarks": "..."}`
- **Response:** `200 OK` (Resumes pipeline on `APPROVED`, terminates on `REJECTED`).

---

## 4. GIS & Spatial Validation (`/api/v1/gis`)

### `POST /api/v1/gis/validate`
Performs topological polygon boundary intersection against authoritative cadastral parcels.
- **Request:** `{"document_id": 1}`
- **Response:** `200 OK` `{"spatial_relationship": "IDENTICAL"|"OVERLAPPING", "overlap_area_sqm": 0.0, "risk_score": 5.0}`

### `GET /api/v1/gis/map-data/{document_id}`
Returns privacy-isolated GeoJSON geometries for deed candidate boundary and adjacent parcels.

---

## 5. Zero-Knowledge Privacy (`/api/v1/privacy`)

### `POST /api/v1/privacy/commitments/generate`
Derives identity scalar and computes algebraic Poseidon commitment over BN254 field.

### `POST /api/v1/privacy/proofs/generate`
Generates zero-knowledge Groth16 proof demonstrating title compliance with zero PII exposure.

---

## 6. Blockchain Registry (`/api/v1/blockchain`)

### `POST /api/v1/blockchain/anchor`
Submits verification hash and ZK commitment to Polygon smart contract.

### `GET /api/v1/blockchain/query/{verification_id}`
Queries on-chain transaction receipt, block number, and confirmation timestamp.

---

## 7. Certificates & Public Portal (`/api/v1/certificates` & `/api/v1/public`)

### `POST /api/v1/certificates/generate`
Generates ReportLab PDF verification certificate with embedded QR code.

### `POST /api/v1/certificates/{id}/revoke`
Revokes certificate (Restricted to Sub-Registrars and Admins).

### `POST /api/v1/certificates/{certificate_number}/verify-integrity`
Verifies byte-level SHA-256 integrity of an uploaded certificate PDF file.

### `GET /api/v1/public/verify/{verification_id}`
Open, unauthenticated public verification endpoint queried by QR code scanners.
- **Response:** `200 OK` `{"status": "VERIFIED", "document_integrity": "PASSED", "spatial_validation": "PASSED", "blockchain_anchor": "CONFIRMED", "blockchain_transaction_hash": "0x...", "disclaimer": "..."}`
