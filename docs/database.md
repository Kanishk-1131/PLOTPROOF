# PlotProof Database Schema & Data Dictionary

PlotProof uses **PostgreSQL 16** with the **PostGIS 3.4** spatial extension.

---

## 1. Entity-Relationship Overview
```
users (1) ───◄ documents (N) ───◄ verifications (1)
                     │                 │
                     ├─◄ ocr_fields    ├─◄ spatial_validations
                     ├─◄ processing_jobs├─◄ integrity_records
                     │                 ├─◄ zk_proofs
                     │                 ├─◄ blockchain_anchors
                     │                 └─◄ certificates
                     ▼
                 audit_events
```

---

## 2. Table Specifications

### 2.1 `users`
Stores user identities and RBAC roles.
- `id` (PK, Integer, Auto-increment)
- `email` (String 255, Unique, Index, Not Null)
- `password_hash` (String 255, Argon2id Hash, Not Null)
- `full_name` (String 255, Not Null)
- `phone` (String 50, Nullable)
- `role` (Enum: `CITIZEN`, `REGISTRAR`, `BANK_OFFICER`, `LAWYER`, `AUDITOR`, `ADMIN`, Not Null)
- `is_active` (Boolean, Default True)
- `created_at` (Timestamp with Timezone, Default NOW())

### 2.2 `documents`
Stores metadata and cryptographic fingerprints of uploaded land title deeds.
- `id` (PK, Integer, Auto-increment)
- `owner_user_id` (FK `users.id`, Index, OnDelete Cascade)
- `file_name` (String 255, Not Null)
- `mime_type` (String 100, Not Null)
- `file_size` (Integer, Bytes, Not Null)
- `storage_key` (String 500, MinIO object path, Not Null)
- `sha256` / `file_hash` (String 64, SHA-256 Digest, Index, Not Null)
- `status` (Enum: `QUEUED`, `PROCESSING`, `PROCESSED`, `FAILED`, `ARCHIVED`)
- `version` (Integer, Default 1)
- `verification_id` (String 100, Unique, Index, Not Null)
- `ocr_raw_text` (Text, Nullable)

### 2.3 `verifications`
Central orchestration state machine entity.
- `id` (PK, Integer, Auto-increment)
- `verification_id` (String 100, Unique, Index, Not Null)
- `document_id` (FK `documents.id`, Unique, OnDelete Cascade)
- `status` (String 50: `UPLOADED`, `PROCESSING`, `OCR_COMPLETED`, `GIS_COMPLETED`, `INTEGRITY_COMPLETED`, `REVIEW_REQUIRED`, `ZK_VERIFIED`, `BLOCKCHAIN_CONFIRMED`, `VERIFIED`, `REJECTED`, `FAILED`)
- `current_stage` (String 50)
- `stages_json` (JSON / Dict: stage statuses)
- `collision_detected` (Boolean, Default False)
- `tamper_detected` (Boolean, Default False)
- `review_required` (Boolean, Default False)
- `review_reason` (Text, Nullable)
- `reviewed_by` (FK `users.id`, Nullable)
- `reviewed_at` (Timestamp, Nullable)
- `review_decision` (String 50: `APPROVED`, `REJECTED`, Nullable)

### 2.4 `parcels`
Authoritative cadastral reference parcel geometries (Read-Only dataset).
- `id` (PK, Integer, Auto-increment)
- `survey_number` (String 100, Index, Not Null)
- `district` (String 100, Not Null)
- `taluk` (String 100, Not Null)
- `village` (String 100, Not Null)
- `area_sq_m` (Float, Standardized Square Meters, Not Null)
- `geometry` (PostGIS `Geometry(POLYGON, 4326)` / WKT Text, Spatial Index, Not Null)

### 2.5 `spatial_validations`
Persists topological intersection results.
- `id` (PK, Integer, Auto-increment)
- `document_id` (FK `documents.id`, OnDelete Cascade)
- `parcel_id` (FK `parcels.id`, Nullable)
- `geometry_valid` (Boolean, Not Null)
- `overlap_detected` (Boolean, Not Null)
- `overlap_area_sq_m` (Float, Not Null)
- `overlap_percentage` (Float, Not Null)
- `area_difference_percent` (Float, Not Null)
- `spatial_relationship` (String 50: `IDENTICAL`, `WITHIN`, `TOUCHING`, `OVERLAPPING`, `DISJOINT`)
- `risk_score` (Float, 0.0 to 100.0)
- `candidate_geojson` (Text, GeoJSON representation)

### 2.6 `integrity_records`
Cryptographic hash fingerprints and RFC 8785 stage chain hashes.
- `id` (PK, Integer, Auto-increment)
- `document_id` (FK `documents.id`, OnDelete Cascade)
- `file_hash` (String 64, SHA-256)
- `ocr_hash` (String 64, SHA-256)
- `metadata_hash` (String 64, SHA-256)
- `spatial_hash` (String 64, SHA-256)
- `verification_hash` (String 64, Combined SHA-256 Chain)

### 2.7 `zk_proofs`
Zero-knowledge proof parameters and algebraic commitments.
- `id` (PK, Integer, Auto-increment)
- `document_id` (FK `documents.id`, OnDelete Cascade)
- `verification_id` (String 100, Index)
- `commitment` (String 100, Poseidon hash on BN254)
- `proof_json` (Text, Groth16 Snarkjs proof payload)
- `public_signals_json` (Text, Public inputs array)
- `status` (String 50: `VERIFIED`, `REJECTED`)

### 2.8 `blockchain_anchors`
On-chain transaction receipts on Polygon L2.
- `id` (PK, Integer, Auto-increment)
- `document_id` (FK `documents.id`, OnDelete Cascade)
- `verification_id` (String 100, Unique, Index)
- `transaction_hash` (String 100, Index)
- `block_number` (Integer, Nullable)
- `contract_address` (String 100)
- `network` (String 50, e.g. `polygon-amoy-testnet`)
- `status` (String 50: `CONFIRMED`, `PENDING`, `FAILED`)

### 2.9 `certificates`
Official verification certificates issued to citizens.
- `id` (PK, Integer, Auto-increment)
- `document_id` (FK `documents.id`, OnDelete Cascade)
- `verification_id` (String 100, Unique, Index)
- `certificate_number` (String 100, Unique, Index)
- `certificate_hash` (String 64, SHA-256 of PDF bytes)
- `file_path` (String 500)
- `status` (String 50: `ACTIVE`, `REVOKED`)
- `revocation_reason` (Text, Nullable)
- `revoked_by` (FK `users.id`, Nullable)

### 2.10 `audit_events`
Append-only forensic compliance trail.
- `id` (PK, Integer, Auto-increment)
- `actor_id` (FK `users.id`, Nullable)
- `document_id` (Integer, Index, Nullable)
- `action` (String 100, e.g. `DOCUMENT_UPLOAD`, `GIS_COLLISION_DETECTED`, `SUB_REGISTRAR_APPROVAL`, `BLOCKCHAIN_ANCHORED`)
- `ip_address` (String 50)
- `timestamp` (Timestamp with Timezone, Default NOW())
- `details_json` (Text, JSON audit payload)
