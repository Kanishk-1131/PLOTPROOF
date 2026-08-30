# PlotProof Demonstration & Presentation Guide

## 1. Ten-Step Presentation Flow for Evaluators

1. **Step 1 — The Problem:** Manual land verification suffers from fragmented paper deeds, uncoordinated spatial boundaries, registry tampering risks, and citizen privacy exposure.
2. **Step 2 — Upload Deed:** Citizen logs in and uploads an unstructured PDF title deed.
3. **Step 3 — Automatic Extraction:** PlotProof extracts survey number (`142/3A`), area (`2400 Sq.ft / 222.96 m²`), location (`Selaiyur, Tambaram`), and GPS coordinates (`12.9252 N, 80.1475 E`).
4. **Step 4 — GIS Spatial Map:** Candidate plot is rendered over the state cadastral layer. No boundary collision detected (`0.0 sq.m overlap`).
5. **Step 5 — Cryptographic Fingerprint:** Multi-stage SHA-256 hash chain is computed deterministically under RFC 8785 canonical JSON.
6. **Step 6 — Zero-Knowledge Privacy:** Generates a Groth16 ZK-SNARK proof on BN254, proving title eligibility without revealing citizen Aadhaar, name, or phone.
7. **Step 7 — Polygon Blockchain Anchor:** Hashes are immutably anchored on Polygon L2 testnet with verifiable transaction receipt.
8. **Step 8 — Certificate Issuance:** Generates a tamper-evident PDF certificate with official statutory legal disclaimer.
9. **Step 9 — Public QR Verification:** Scan the QR code using any phone camera to access the public verification portal.
10. **Step 10 — Outcome:** `✓ VERIFIED` with full cryptographic audit trail.

---

## 2. Three Controlled Demonstration Scenarios

### DEMO-001: Clean Deed (The Happy Path)
- **Scenario:** Valid deed for Survey 142/3A.
- **Workflow:** Ingestion &rarr; OCR &rarr; GIS &rarr; Integrity &rarr; ZK &rarr; Blockchain &rarr; Certificate &rarr; QR Portal.
- **Result:** `✓ VERIFIED`.

### DEMO-002: Spatial Boundary Collision (The Encroachment Intercept)
- **Scenario:** Deed claiming expanded 3,400 sq.ft encroaching on adjacent plot.
- **Workflow:** GIS detects 17.8 sq.m overlap &rarr; Pipeline halts at `REVIEW_REQUIRED`.
- **Key Point:** Proves PlotProof is not merely hashing PDFs; it understands physical geography. No blockchain anchor or certificate is issued without Sub-Registrar approval.

### DEMO-003: Single-Bit Document Tampering (The Cryptographic Defense)
- **Scenario:** Single character modified in deed text after verification baseline.
- **Workflow:** SHA-256 byte comparison detects mismatch against stored hash.
- **Result:** `✗ HASH MISMATCH / INTEGRITY FAILED`.

---

## 3. What NOT to Claim vs What TO Claim

| ✗ Do NOT Claim (Scientifically Inaccurate) | ✓ DO Claim (Technically Defensible) |
|:---|:---|
| *"AI guarantees 100% fraud detection"* | *"Multi-vector automated anomaly detection & spatial conflict interception"* |
| *"Blockchain makes land legally authentic"* | *"Immutable on-chain verification anchoring & tamper-evident audit logging"* |
| *"Eliminates government land registrars"* | *"Empowers Sub-Registrars with automated intelligence while preserving statutory authority"* |
| *"Zero-knowledge hides everything"* | *"Proves title verification conditions while strictly preventing citizen PII leakage"* |
