# Architecture Specification — PLOTPROOF

## System Architecture

```
                    ┌─────────────────────────┐
                    │     Next.js 14 App      │
                    │   React 18 / Tailwind   │
                    └───────────┬─────────────┘
                                │
                         REST + Bearer JWT
                                │
                                ▼
                    ┌─────────────────────────┐
                    │      FastAPI App        │
                    │   Orchestrator & Auth   │
                    └───────────┬─────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Document Service │  │   GIS Engine     │  │  Trust Service   │
│  - OpenCV/Pillow │  │  - Shapely 2.0   │  │  - SHA-256       │
│  - Field Extract │  │  - GeoPandas     │  │  - Polygon Amoy  │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                    ┌─────────────────────────┐
                    │    SQLAlchemy 2.0       │
                    │   SQLite (Dev) / PostGIS│
                    └─────────────────────────┘
```

## Security & Identity (Layer 2)
- **Password Protection**: Argon2id via `pwdlib`. Passwords are never stored in plaintext.
- **Session Tokens**: Short-lived (15 min) HS256 JWT access tokens containing user ID and role claims.
- **Refresh Tokens**: Stored as SHA-256 hashes in database with strict single-use rotation (preventing replay attacks) and explicit revocation on logout.
- **Role-Based Access Control**: Decorators and dependency checkers (`require_roles(...)`) enforce route access for CITIZEN, REGISTRAR, BANK_OFFICER, and ADMIN.
- **Audit Logging**: All registration, login, logout, and token rotation actions are committed to an immutable `audit_logs` table recording user ID, action, resource type, IP address, and timestamp.

## GIS Cadastral Engine
- Parcels are represented as planar 2D polygons in EPSG:4326.
- Encroachment detection performs intersection calculus (`plot_a.intersection(plot_b)`).
- Area computation accurately translates square degrees into metric $m^2$ and Indian standard $sq.ft$ extents.

## Blockchain Trust Layer
- Deterministic canonical JSON representation hashed with SHA-256.
- Records anchored into EVM smart contract `PlotProofRegistry.sol` emitting `TitleRegistered(bytes32 indexed documentHash, string verificationId, address indexed authority)`.
