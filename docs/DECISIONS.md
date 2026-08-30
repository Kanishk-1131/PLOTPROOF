# Architecture Decision Records (ADRs) — PLOTPROOF

## ADR 001: Hybrid Database Architecture (SQLite Dev / PostgreSQL + PostGIS Production)
- **Status**: Accepted
- **Context**: Hackathon evaluation and local developer machines often do not have Docker or PostGIS pre-installed. The system must run flawlessly out-of-the-box on developer laptops with zero external database daemons.
- **Decision**: Use SQLAlchemy 2.0 with unified engine configurations that default to zero-config local SQLite for instant runtime, while supporting full PostgreSQL + PostGIS via `DATABASE_URL` in containerized/production environments.
- **Tradeoffs**: PostGIS spatial SQL operators (`ST_Intersects`) are mirrored in Python using Shapely for SQLite environments, guaranteeing identical high-precision boundary intersection calculations.

## ADR 002: Token Rotation & Refresh Token Hashing (Layer 2)
- **Status**: Accepted
- **Context**: Long-lived access tokens or plaintext refresh tokens in databases present severe attack vectors.
- **Decision**: Issue 15-minute access tokens and 7-day refresh tokens. The database only ever stores the SHA-256 hash of refresh tokens. Every call to `/refresh` invalidates the old token and issues a new pair (Token Rotation), automatically detecting and blocking replay attacks.
- **Consequences**: Enhanced security, immune to credential theft from database dumps.

## ADR 003: Public Verification Portal with Zero Auth Friction
- **Status**: Accepted
- **Context**: Bank officers, buyers, and legal auditors must be able to scan QR codes on printed physical certificates and instantly inspect the title status without creating an account or hitting a paywall.
- **Decision**: Implement `/api/public/verify/{document_hash}` and frontend `/verify/[hash]` as a public read-only portal while keeping document ingestion and registrar approvals strictly behind RBAC authorization boundaries.
