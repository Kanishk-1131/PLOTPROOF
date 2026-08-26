# PLOTPROOF — Digital Land Title & Cadastral Verification Platform

> **Forensic-Grade Land Title Verification & Tamper-Evident Cadastral Registry**  
> *Built for Smart India Hackathon (SIH)*

---

## 1. System Overview

PlotProof solves illegal land encroachment, double-registration, and forged title deeds by combining **Document Intelligence (OpenCV & OCR)**, **GIS Cadastral Spatial Analysis (PostGIS / Shapely)**, **Trust & Tamper Detection (Canonical SHA-256 + Smart Contracts)**, and **Privacy Preservation (PII Minimization & ZK-Commitments)** into an automated forensic audit pipeline.

```
                         PLOTPROOF
                            │
                            ▼
                    ┌───────────────┐
                    │   NEXT.JS UI  │
                    └───────┬───────┘
                            │
                         REST API
                            │
                            ▼
                    ┌───────────────┐
                    │ FASTAPI       │
                    │ ORCHESTRATOR  │
                    └───────┬───────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
   DOCUMENT SERVICE    GIS SERVICE      TRUST SERVICE
          │                 │                 │
          ▼                 ▼                 ▼
      OpenCV/OCR        GeoPandas          SHA-256
          │                 │                 │
          ▼                 ▼                 ▼
   Field Extraction      PostGIS          Blockchain
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
                     VERIFICATION ENGINE
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
          PASS           WARNING          FAIL
             │
             ▼
       CERTIFICATE
             │
             ▼
          QR CODE
             │
             ▼
      PUBLIC VERIFY PAGE
```

---

## 2. The 4 Engineering Pillars

| Pillar | Technology | Role in Pipeline |
| :--- | :--- | :--- |
| **Module A: Document Intelligence** | OpenCV, Python, Regex Rule Engine | Image preprocessing (deskew, bilateral noise filter, Otsu thresholding), layout parsing, and structured extraction into standardized Land Record JSON. |
| **Module B: GIS Spatial Intelligence** | Shapely, GeoPandas, PostGIS, Leaflet | Spatial bounding polygon reconstruction, topological `ST_Intersects` and `ST_Overlaps` queries, overlap area calculation in $m^2$ & $sq.ft$, and collision visualization. |
| **Module C: Trust & Tamper Detection** | Canonical JSON, SHA-256, Solidity Smart Contract | Computes deterministic document cryptographic fingerprints. Triggers instant hash mismatch alerts when deed parameters are modified post-registration. |
| **Module D: Privacy & ZK Proofs** | Pedersen / HMAC Commitments, PII Masking | Validates titleholder identity without ever exposing citizen Aadhaar, phone numbers, or residential addresses on public ledgers. |

---

## 3. Live Demonstration Scenarios

PlotProof includes **3 pre-calibrated live demonstration test cases** built directly into the UI:

### Demo 1 — Genuine Title Deed (Survey 142/3A)
- **Input**: `sample_genuine_142_3A.txt` / PDF
- **Pipeline**: Ingests deed &rarr; Preprocessing & OCR &rarr; Validates zero spatial collisions &rarr; SHA-256 hash `7c3e8f2c...` &rarr; Anchors on Polygon Blockchain.
- **Verdict**: `✓ VERIFIED` (Confidence: 99.2%)
- **Output**: Generates verifiable Digital Certificate with QR code. Scanning the QR opens the independent `/verify/[hash]` public portal.

### Demo 2 — Tampered Deed (Forged Area Extent)
- **Input**: `sample_tampered_area.txt` / PDF (Area changed from 2400 sq.ft to 3400 sq.ft)
- **Pipeline**: OCR extracts 3400 sq.ft &rarr; Canonical JSON hash differs from registered baseline &rarr; Triggers tamper interception.
- **Verdict**: `⚠ DOCUMENT INTEGRITY TAMPER ALERT` (Confidence: 38%)

### Demo 3 — Spatial Collision (Boundary Encroachment)
- **Input**: `sample_collision_142_3B.txt` / PDF
- **Pipeline**: Reconstructs polygon for Survey 142/3B &rarr; GIS engine detects intersection against registered Survey 142/3A &rarr; Computes **17.8 sq.m (191.6 sq.ft)** encroached overlap.
- **Verdict**: `⚠ SPATIAL COLLISION DETECTED` (Risk: HIGH)
- **Map View**: Highlights conflicting parcel boundary in red on the interactive Leaflet GIS map.

---

## 4. Quickstart: Running Locally

### Step 1: Run the Backend
```bash
cd backend
python -m pip install -r requirements.txt
python app/main.py
```
> The backend server starts at **`http://localhost:8000`** and automatically seeds the database with cadastral parcels and test deeds. API Swagger docs are available at `http://localhost:8000/docs`.

### Step 2: Run the Frontend
```bash
cd frontend
npm install
npm run dev
```
> The Next.js application will be live at **`http://localhost:3000`**.

---

## 5. Project Folder Structure

```
plotproof/
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                     # Landing page & demo launcher
│   │   ├── dashboard/page.tsx           # Land Verification Command Center
│   │   ├── upload/page.tsx              # Upload & 6-stage live stepper
│   │   ├── verification/[id]/page.tsx   # Forensic Verification Report
│   │   ├── map/page.tsx                 # Fullscreen GIS Cadastral Map
│   │   ├── certificate/[id]/page.tsx    # Digital Certificate with QR
│   │   └── verify/[hash]/page.tsx       # Public QR Trust Portal
│   ├── components/
│   │   ├── Navbar.tsx
│   │   └── MapView.tsx                  # Leaflet interactive GIS component
│   └── services/
│       └── api.ts                       # Typed Axios API Client
│
├── backend/
│   ├── app/
│   │   ├── main.py                      # FastAPI orchestrator entrypoint
│   │   ├── api/                         # REST API endpoints
│   │   ├── services/                    # OCR, GIS, Hash, ZK, & Certificate services
│   │   ├── models/                      # SQLAlchemy database models
│   │   ├── schemas/                     # Pydantic request/response schemas
│   │   └── database/                    # Connection & DB engine
│   └── static/                          # Static uploads & generated QR certificates
│
├── blockchain/
│   ├── contracts/
│   │   └── PlotProofRegistry.sol        # Solidity registry smart contract
│   └── hardhat.config.js
│
└── docker-compose.yml                   # Containerized full-stack deployment
```
