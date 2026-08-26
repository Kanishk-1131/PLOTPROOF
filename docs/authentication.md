# PlotProof Authentication & Access Control

## 1. Password Hashing
PlotProof strictly uses **Argon2id** (via `pwdlib`) for password storage:
- Memory cost: 65,536 KiB (64 MB)
- Time cost: 3 iterations
- Parallelism: 4 lanes
- Immune to GPU/ASIC rainbow table cracking

---

## 2. JWT Token Architecture
Tokens use HMAC-SHA256 (`HS256`) with strict minimal claims hygiene:
```json
{
  "sub": "42",
  "role": "CITIZEN",
  "type": "access",
  "exp": 1756200000
}
```
**Zero-PII Token Envelope:** Citizen Aadhaar, email, full name, phone number, and private keys are never placed inside the JWT token.

---

## 3. Token Lifecycle & Rotation
1. **Access Token:** Valid for 60 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES`).
2. **Refresh Token:** Cryptographically secure 48-byte random token (`secrets.token_urlsafe(48)`), hashed with SHA-256 in the database, valid for 7 days (`REFRESH_TOKEN_EXPIRE_DAYS`).
3. **Rotation:** Upon refresh, the old refresh token is revoked and a new pair is issued (Single-Use Refresh Tokens).

---

## 4. Role-Based Access Control (RBAC) Matrix

| Operation | CITIZEN | REGISTRAR | BANK_OFFICER | LAWYER | AUDITOR | ADMIN |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Upload Deed** | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| **View Own Documents** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **View All Documents** | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| **Trigger Verification** | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| **Review Queue (Approve/Reject)** | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| **Manual Field Correction** | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| **Generate Certificate** | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ |
| **Revoke Certificate** | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ |
| **View Audit Trail** | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ |
| **System Settings** | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Public QR Verification** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
