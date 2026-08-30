# PlotProof Quickstart & Setup Guide

## 1. Prerequisites
- **Docker & Docker Compose** (v24.0+ recommended)
- **Python** (v3.11+)
- **Node.js** (v18+ or v20 LTS)
- **Git**

---

## 2. One-Command Docker Startup
To launch the complete multi-container system (PostgreSQL + PostGIS, Redis, FastAPI Backend, Celery Worker, Next.js Frontend, MinIO, ClamAV, Nginx):

```bash
# 1. Clone repository
git clone https://github.com/your-org/plotproof.git
cd plotproof

# 2. Configure environment
cp .env.example .env

# 3. Build and launch all services
docker compose up --build -d
```

### Verification Endpoints:
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000)
- **Backend API & Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Technical Reference:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)
- **Readiness Probe:** [http://localhost:8000/ready](http://localhost:8000/ready)

---

## 3. Local Development Setup (Without Docker)

### Backend Setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Pre-seed cadastral parcels and test deeds
python -c "from app.seed_data.seed_db import seed_database; seed_database()"

# Start development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```

---

## 4. Running the Test Suite
PlotProof includes 50+ master tests across Unit, Integration, Security, and E2E categories:

```bash
# Run all tests
make test
# Or using unittest directly:
python -m unittest discover -s tests -p "test_*.py"

# Category-specific test runs:
make test-unit
make test-integration
make test-security
make test-e2e
```

---

## 5. Seeded Accounts & Credentials

| Role | Email | Password | Permissions |
|:---|:---|:---|:---|
| **Citizen** | `citizen@plotproof.gov.in` | `CitizenPass123!` | Upload deed, track personal verifications, download certificates. |
| **Sub-Registrar** | `registrar@tn.gov.in` | `RegistrarPass123!` | Review queue, approve/reject boundary variances, revoke certificates. |
| **Bank Officer** | `bank@sbi.co.in` | `BankPass123!` | Inspect verified audit trails, download collateral verification certificates. |
| **Admin** | `admin@plotproof.gov.in` | `AdminPass123!` | System configuration, audit logs, node status monitoring. |
