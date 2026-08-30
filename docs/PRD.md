# Product Requirements Document (PRD) — PLOTPROOF

## Problem
In India and developing economies, land disputes represent over 66% of all civil litigation. Fraudulent double-registration of titles, forged boundary extents, encroached parcel boundaries, and opaque paper registries lead to billions in lost capital and stalled infrastructure.

## Target Users
1. **Citizen / Landowner**: Verifies authenticity of title deeds, checks encroaching overlaps prior to purchase, and stores cryptographically sealed ownership records.
2. **Sub-Registrar (Government Authority)**: Performs automated forensic inspection of incoming deed transfers, compares cadastral GIS boundary geometry, verifies SHA-256 digital seals, and prevents illegal double-registration.
3. **Bank Loan / Mortgage Audit Officer**: Evaluates land collateral authenticity, checks legal encumbrances, and validates that title deeds have not been forged or mortgaged across multiple financial institutions.
4. **System Administrator / Network Operator**: Manages cryptographic verification services, monitors blockchain anchor status, and audits forensic security trails.

## Proposed Solution
PlotProof is a multi-vector automated land title deed verification platform integrating:
- **Document Intelligence (OpenCV & OCR)**: Image deskewing, Otsu binarization, noise filtering, and structured field extraction.
- **GIS Cadastral Spatial Analysis (Shapely & GeoPandas)**: Spatial polygon reconstruction, topological intersection checks against government cadastral layers, and precise encroachment area calculations in $m^2$ and $sq.ft$.
- **Cryptographic Trust & Blockchain Anchoring**: Canonical JSON hashing and immutable Ethereum/Polygon smart contract timestamping.
- **Privacy Preservation**: Zero-Knowledge / Pedersen commitments and Aadhaar/PII masking so no citizen private data is leaked on-chain.
- **Tamper-Evident QR Digital Certificate**: Portable PDF certificate with embedded cryptographic QR code linkable to a public verification ledger.

## Core Features
1. **Multi-Role Authentication & Access Control (Layer 2)**:
   - Argon2id password hashing with anti-privilege escalation (citizens default to `CITIZEN` role).
   - JWT access tokens (15m) and cryptographically hashed refresh token rotation (7d).
   - Role-Based Access Control (RBAC) across Citizen, Registrar, Bank Officer, and Admin.
   - Comprehensive tamper-evident security audit logging.
2. **Automated Forensic Verification Pipeline**:
   - Ingestion of deeds (PDF / image / pre-calibrated test cases).
   - Real-time 6-stage verification stepper in the Next.js UI.
   - Forensic report detailing confidence score, spatial collisions, hash authenticity, and privacy metrics.
3. **Interactive Cadastral GIS Map**:
   - Leaflet map rendering cadastral parcel layers with interactive inspection.
   - Visual highlighting of encroached overlap polygons in red warning overlays.
4. **Verifiable Digital Certificate & Public Trust Portal**:
   - Generates signed QR certificate.
   - Public verification portal (`/verify/[hash]`) requiring zero login for bank auditors and prospective buyers.

## MVP Success Criteria
- [x] Zero-barrier demonstration: 3 pre-calibrated test deeds (Genuine, Tampered Area, Spatial Collision).
- [x] Working end-to-end pipeline from upload to on-chain hash verification and PDF certificate.
- [x] Sub-2 second verification runtime.
- [x] Complete production-grade auth and audit trail.
