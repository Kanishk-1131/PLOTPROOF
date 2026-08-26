# PlotProof Production Deployment Runbook

## 1. Environments
- **Development:** Local Docker Compose (`docker compose up`)
- **Staging:** Kubernetes / Cloud VM with Polygon Amoy Testnet
- **Production:** High-Availability Cluster with Polygon Mainnet, TLS 1.3, Read-Replicas for PostgreSQL, Distributed Redis.

---

## 2. Zero-Downtime Migration Procedure
Never execute `DROP DATABASE` or raw table resets in production.

```bash
# 1. Take snapshot backup
pg_dump -U plotproof -d plotproof -F c -b -v -f "/backups/backup_$(date +%Y%m%d_%H%M%S).dump"

# 2. Run forward Alembic migration
alembic upgrade head

# 3. Verify migration status
alembic current
```

---

## 3. Production ASGI Tuning
- Run Uvicorn workers behind Gunicorn:
```bash
gunicorn -k uvicorn.workers.UvicornWorker \
  -w 4 \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --graceful-timeout 30 \
  app.main:app
```
- Formula for worker count: `(2 * CPU_CORES) + 1`.

---

## 4. Disaster Recovery & Backup Plan
- **Database:** Automated daily PostgreSQL WAL archiving and pg_dump snapshots.
- **Storage:** MinIO / AWS S3 Cross-Region Bucket Replication.
- **Blockchain:** Self-healing on-chain ledger; immutable once anchored.
- **Recovery Time Objective (RTO):** < 15 minutes.
- **Recovery Point Objective (RPO):** < 1 hour.
