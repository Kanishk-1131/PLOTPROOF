# PlotProof System Architecture

## 1. System Overview
**PlotProof** is an automated, tamper-evident land record digitization, spatial validation, cryptographic integrity, zero-knowledge privacy, and blockchain anchoring platform.

```
Citizen / Registrar / Bank
         │
         ▼
   Next.js Frontend (Port 3000)
         │  (HTTPS / TLS 1.3)
         ▼
   Nginx Reverse Proxy (Port 80/443)
         │
         ▼
   FastAPI API Gateway (Port 8000)
         │
 ┌───────┴─────────────────────────────────────────────┐
 │ Central Verification State Machine                  │
 │                                                     │
 │ 1. Document Ingestion  ──► Malware & Magic Bytes    │
 │ 2. OCR Intelligence   ──► EasyOCR + Tesseract      │
 │ 3. GIS Spatial Engine  ──► Shapely + PostGIS        │
 │ 4. Cryptographic Hash  ──► SHA-256 + RFC 8785 Chain │
 │ 5. Zero-Knowledge ZK   ──► Poseidon + BN254 Groth16 │
 │ 6. Polygon Blockchain  ──► Solidity Registry L2     │
 │ 7. Certificate Engine  ──► PDF + QR Code PNG        │
 │ 8. Public Trust Portal ──► Instant QR Verification  │
 └─────────────────────────────────────────────────────┘
         │                          │
         ▼                          ▼
 PostgreSQL + PostGIS (5432)   Redis Queue (6379)
         │                          │
         ▼                          ▼
 MinIO Object Storage (9000)   Async Processing Worker
```

---

## 2. Central Verification State Machine
All land documents transition through one deterministic state machine:

```
[UPLOADED]
    │
    ▼
[PROCESSING]
    │
    ▼
[OCR_COMPLETED]
    │
    ▼
[GIS_COMPLETED]
    │
    ├── (Spatial Collision / Overlap) ──► [REVIEW_REQUIRED]
    │                                          │
    │                    ┌─────────────────────┴───────────────────┐
    │                    ▼                                         ▼
    │           [APPROVED (Registrar)]                    [REJECTED (Registrar)]
    │                    │                                         │
    │                    ▼                                         ▼
    └──► [INTEGRITY_COMPLETED]                             (Pipeline Terminated)
                 │
                 ▼
          [READY_FOR_PROOF]
                 │
                 ▼
           [ZK_VERIFIED]
                 │
                 ▼
        [BLOCKCHAIN_PENDING]
                 │
                 ▼
        [BLOCKCHAIN_CONFIRMED]
                 │
                 ▼
        [CERTIFICATE_GENERATED]
                 │
                 ▼
             [VERIFIED]
```

---

## 3. Subsystem Breakdown

| Subsystem | Technology | Responsibility |
|:---|:---|:---|
| **Frontend** | Next.js 14, React 18, TailwindCSS, Lucide Icons, Leaflet GIS | Responsive citizen dashboard, Sub-Registrar review queue, interactive GIS map viewer, and QR verification portal. |
| **API Gateway** | FastAPI, Pydantic v2, Python 3.11 | High-throughput REST API with JWT authentication, role-based access control (RBAC), and request-ID tracing. |
| **Document Ingestion** | MinIO S3, ClamAV, Magic Bytes | File signature sniffing, antivirus scanning, SHA-256 duplicate fingerprinting, and AES-256-GCM storage quarantine. |
| **OCR Intelligence** | EasyOCR, Tesseract OCR, OpenCV, PyMuPDF | Multilingual extraction (English + Tamil), adaptive thresholding, deskew orientation correction, and entity normalization. |
| **GIS Engine** | Shapely, GeoPandas, PostGIS (EPSG:32644 / EPSG:4326) | Coordinate reprojection, metric polygon construction, cadastral boundary overlap detection, and area consistency scoring. |
| **Integrity Engine** | SHA-256, RFC 8785 Canonical JSON | Byte-level file hashing, canonical key sorting, and cryptographic hash chain stage linkage. |
| **ZK Privacy Engine** | Circom 2.1, Snarkjs, Poseidon Hashing, BN254 Curve | Zero-knowledge proof generation and verification, hiding citizen PII while mathematically proving title compliance. |
| **Blockchain Anchor** | Solidity 0.8.20, Web3.py, Polygon Amoy Testnet (L2) | Tamper-evident on-chain anchoring of verification hash and ZK commitment. |
| **Certificate Engine**| ReportLab, QRCode PIL | Cryptographically verifiable PDF certificate generation with embedded public QR verification portal link. |
| **Public Portal** | FastAPI Public Endpoints, Next.js Verify Page | Controlled, zero-PII public verification interface for banks, buyers, and legal counsel. |
