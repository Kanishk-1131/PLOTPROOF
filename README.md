# PLOTPROOF

> **Multi-Vector Intelligent Land Title Digitization, Spatial Validation, Zero-Knowledge Privacy & Blockchain Verification Platform**

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14.2-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![PostgreSQL PostGIS](https://img.shields.io/badge/PostGIS-3.4-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgis.net)
[![Polygon L2](https://img.shields.io/badge/Polygon-Amoy-8247E5?style=for-the-badge&logo=polygon&logoColor=white)](https://polygon.technology)
[![Zero Knowledge](https://img.shields.io/badge/ZK--SNARK-Groth16%20%2F%20BN254-orange?style=for-the-badge)](https://circom.io)
[![Tests Passing](https://img.shields.io/badge/Tests-173%20Passed%20(100%25)-brightgreen?style=for-the-badge)]()

---

## 1. Problem Statement
Manual land title verification in India faces critical challenges:
1. **Physical Deed Tampering:** Scanned deed alterations and fabricated sale deeds.
2. **Spatial Encroachment:** Boundary overlap and double-registration across identical survey numbers.
3. **Citizen Privacy Exposure:** Public land records exposing citizen Aadhaar, phone numbers, and addresses.
4. **Siloed Registries:** Banks, buyers, and registrars lack an instant, tamper-evident verification anchor.

---

## 2. The PlotProof Solution
PlotProof is an automated 8-stage verification pipeline that transforms unstructured paper deeds into cryptographically secured, spatially validated digital land titles:

```
Citizen / Registrar
        │
        ▼
 1. Document Ingestion  ──► Antivirus Scan, Magic Bytes Sniffing & SHA-256 Quarantine
        │
        ▼
 2. OCR Intelligence   ──► Dual Engine (EasyOCR + Tesseract), Deskew & Unit Normalization
        │
        ▼
 3. GIS Spatial Engine  ──► PostGIS Polygon Intersection & Cadastral Overlap Detection
        │
        ├── (Encroachment Detected) ──► Sub-Registrar Statutory Manual Review Hold
        │
        ▼
 4. Cryptographic Hash  ──► RFC 8785 Canonical JSON & Multi-Stage Linked Hash Chain
        │
        ▼
 5. Zero-Knowledge ZK   ──► Poseidon Commitments & BN254 Groth16 zk-SNARK (Zero Citizen PII)
        │
        ▼
 6. Polygon Blockchain  ──► Immutable Smart Contract Anchoring on Polygon L2
        │
        ▼
 7. Certificate Engine  ──► Tamper-Evident ReportLab PDF + Pure URL Verification QR Code
        │
        ▼
 8. Public Portal       ──► Instant Smartphone QR Scan Verification for Banks & Citizens
```

---

## 3. Technology Stack

- **Frontend:** Next.js 14, React 18, TailwindCSS, Lucide React, Leaflet GIS.
- **Backend API:** FastAPI, Pydantic v2, Python 3.11, SQLAlchemy 2.0, Alembic.
- **Spatial & GIS:** PostGIS 3.4, Shapely 2.0, GeoPandas, PyProj (EPSG:32644 / EPSG:4326).
- **OCR Intelligence:** EasyOCR, Tesseract OCR (English & Tamil), OpenCV, PyMuPDF.
- **Privacy & ZK:** Circom 2.1, Snarkjs, Poseidon Hash, BN254 Scalar Field.
- **Blockchain:** Solidity 0.8.20, Web3.py, Polygon Amoy Testnet (L2).
- **Security & Storage:** Argon2id (`pwdlib`), MinIO S3, ClamAV, Redis 7, Nginx.

---

## 4. Quickstart & Installation

### Option A: One-Command Docker Launch (Recommended)
```bash
# Clone repository
git clone https://github.com/your-org/plotproof.git
cd plotproof

# Configure environment
cp .env.example .env

# Build and launch all services
docker compose up --build -d
```

- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Health Probe:** [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Local Development
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python -c "from app.seed_data.seed_db import seed_database; seed_database()"
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Frontend Setup
cd ../frontend
npm install
npm run dev
```

---

## 5. Master Test Suite

PlotProof features **173 automated tests** passing with 100% success:

```bash
# Run complete test suite
make test

# Or run by category:
make test-unit         # 22 Unit tests (Auth, OCR, GIS, Hash, ZK, Blockchain, Cert)
make test-integration  # 9 Integration tests (Pipelines, DB constraints, PostGIS, ZK->Chain)
make test-security     # 13 Security tests (RBAC, IDOR, MIME sniffing, Security Headers)
make test-e2e          # 6 End-to-End & Demo tests (Clean, Collision, Tamper, 16-Point Checklist)
```

---

## 6. Demo Scenarios for Evaluators

1. **DEMO-001 (Clean Deed):** Valid deed for Survey 142/3A &rarr; Full pipeline execution &rarr; `✓ VERIFIED` on Polygon L2.
2. **DEMO-002 (Boundary Collision):** Encroaching deed &rarr; 17.8 sq.m overlap detected &rarr; Halted at `REVIEW_REQUIRED` (No on-chain anchor without Sub-Registrar approval).
3. **DEMO-003 (Single-Bit Tamper):** Modified survey digit &rarr; Intercepted by SHA-256 byte comparison &rarr; `✗ INTEGRITY FAILED`.

---

## 7. Documentation Directory (`/docs`)

Comprehensive documentation is available inside the [`docs/`](file:///c:/PLOTPROOF/docs) folder:
- [System Architecture](file:///c:/PLOTPROOF/docs/architecture.md)
- [Quickstart & Setup](file:///c:/PLOTPROOF/docs/setup.md)
- [Database Data Dictionary](file:///c:/PLOTPROOF/docs/database.md)
- [REST API Reference](file:///c:/PLOTPROOF/docs/api.md)
- [Authentication & RBAC](file:///c:/PLOTPROOF/docs/authentication.md)
- [OCR & Extraction](file:///c:/PLOTPROOF/docs/ocr.md)
- [GIS & Spatial Validation](file:///c:/PLOTPROOF/docs/gis.md)
- [Cryptographic Integrity](file:///c:/PLOTPROOF/docs/integrity.md)
- [Zero-Knowledge Privacy](file:///c:/PLOTPROOF/docs/zk.md)
- [Polygon Smart Contract](file:///c:/PLOTPROOF/docs/blockchain.md)
- [PDF Certificate & QR](file:///c:/PLOTPROOF/docs/certificate.md)
- [Deployment Runbook](file:///c:/PLOTPROOF/docs/deployment.md)
- [Security & Threat Model](file:///c:/PLOTPROOF/docs/security.md)
- [Troubleshooting Runbook](file:///c:/PLOTPROOF/docs/troubleshooting.md)
- [Judge Demonstration Guide](file:///c:/PLOTPROOF/docs/demo.md)

---

## 8. License & Statutory Notice
*PlotProof System Verification Certificates confirm cryptographic verification results produced by the PlotProof platform. They do not independently constitute a government-issued title document. Official statutory determination of property ownership remains subject to competent Sub-Registrar and Revenue Department authority.*
