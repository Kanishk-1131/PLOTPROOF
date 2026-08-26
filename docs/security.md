# PlotProof Security Model & Threat Analysis

## 1. Threat Model & Defensive Mitigations

| Threat | Threat Category (STRIDE) | PlotProof Defensive Mitigation |
|:---|:---|:---|
| **Document Tampering** | Tampering | SHA-256 binary hash + RFC 8785 stage chain anchored immutably to Polygon blockchain. |
| **Unauthorized Access / IDOR** | Elevation of Privilege | Object-level owner validation (`user_id == doc.owner_user_id` or `role == REGISTRAR`). |
| **PII & Aadhaar Leakage** | Information Disclosure | Private witness separation + Poseidon algebraic commitments + Zero citizen PII on-chain. |
| **Malicious File Uploads** | Tampering / Denial of Service | File signature magic bytes sniffing + ClamAV antivirus scanning + 50MB hard boundary. |
| **Replay Attacks** | Spoofing | Single-use rotating refresh tokens + Unique `verification_id` database constraints. |
| **Brute Force & DoS** | Denial of Service | Adaptive IP/Token rate limiting (5 req/min on auth, 20 req/min on pipeline triggers). |

---

## 2. Cryptographic Hygiene & Secret Management
- **Never commit `.env` or private keys to Git.**
- **HS256 JWT Secret:** 256-bit cryptographically secure random string.
- **Argon2id Salt:** Deterministic per-user cryptographic salt generated via `os.urandom`.
- **Blockchain Private Key:** Stored inside Kubernetes KMS / HashiCorp Vault.
