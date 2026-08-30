# PlotProof Troubleshooting & Operational Runbook

## 1. Standard Error Codes Dictionary

| Error Code | HTTP Status | Root Cause & Resolution |
|:---|:---:|:---|
| `DOCUMENT_NOT_FOUND` | 404 | Document ID does not exist in database. |
| `INVALID_FILE_TYPE` | 400 | File extension or MIME signature is not an allowed PDF/TIFF format. |
| `FILE_TOO_LARGE` | 400 | Uploaded deed exceeds the 50MB hard size boundary. |
| `OCR_FAILED` | 500 | Image resolution too degraded for OCR engine. Re-scan at 300 DPI. |
| `OCR_LOW_CONFIDENCE` | 422 | Optical recognition confidence < 75%; routed to Sub-Registrar review. |
| `GIS_VALIDATION_FAILED` | 400 | Invalid self-intersecting polygon geometry. Repaired automatically if salvageable. |
| `SPATIAL_COLLISION_DETECTED` | 409 | Plot boundary overlaps an existing registered cadastral parcel > 0.05m². |
| `INTEGRITY_MISMATCH` | 400 | Document or metadata altered after cryptographic verification baseline. |
| `FRAUD_REVIEW_REQUIRED` | 422 | High risk score detected across multi-vector verification checks. |
| `ZK_PROOF_FAILED` | 500 | Private witness signals failed algebraic circuit constraints. |
| `ZK_VERIFICATION_FAILED` | 400 | Public commitment or verification hash altered prior to proof verification. |
| `BLOCKCHAIN_SUBMISSION_FAILED` | 502 | Polygon RPC node unreachable or wallet insufficient POL balance. |
| `BLOCKCHAIN_CONFIRMATION_TIMEOUT` | 504 | Transaction pending in mempool > 120s due to gas spike. |
| `CERTIFICATE_GENERATION_FAILED` | 500 | ReportLab PDF compilation failure or missing verification prerequisite. |
| `CERTIFICATE_REVOKED` | 410 | Official certificate has been formally revoked by Sub-Registrar. |

---

## 2. Common Operational Diagnostics

### Scenario A: Backend API Unreachable
```bash
# Check container status
docker compose ps
# Inspect backend logs
docker compose logs --tail=100 backend
# Test backend health probe
curl -I http://localhost:8000/health
```

### Scenario B: Database Connection Error
```bash
# Check PostgreSQL container
docker compose logs postgres
# Verify PostGIS extension is loaded
docker compose exec postgres psql -U plotproof -d plotproof -c "SELECT PostGIS_Version();"
```

### Scenario C: OCR Processing Job Stalled
```bash
# Check Redis queue
docker compose exec redis redis-cli ping
# Check Worker container logs
docker compose logs --tail=100 worker
```

### Scenario D: Blockchain Anchoring Pending
```bash
# Check Polygon RPC endpoint connectivity
curl -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' https://rpc-amoy.polygon.technology
```
