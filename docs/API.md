# API Reference — PLOTPROOF

Base URL: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/docs`

---

## 1. Authentication & RBAC (`/api/v1/auth`)

### `POST /api/v1/auth/register`
Creates a new user account. Always assigns `CITIZEN` role.
- **Request**: `{ "email": "string", "password": "string (min 8)", "full_name": "string", "phone": "string?" }`
- **Response**: `200 OK` &rarr; `{ "id": int, "email": "...", "full_name": "...", "role": "CITIZEN", "is_verified": false }`
- **Errors**: `409 Conflict` if email already registered.

### `POST /api/v1/auth/login`
Authenticates with Argon2id password hash and returns tokens.
- **Request**: `{ "email": "...", "password": "..." }`
- **Response**: `200 OK` &rarr; `{ "access_token": "...", "token_type": "bearer", "refresh_token": "...", "user": { ... } }`
- **Errors**: `401 Unauthorized` if invalid credentials.

### `POST /api/v1/auth/refresh`
Rotates refresh token and returns new token pair.
- **Request**: `{ "refresh_token": "..." }`
- **Response**: `200 OK` &rarr; `{ "access_token": "...", "token_type": "bearer", "refresh_token": "...", "user": { ... } }`

### `POST /api/v1/auth/logout`
Revokes active refresh token.
- **Request**: `{ "refresh_token": "..." }`
- **Response**: `200 OK` &rarr; `{ "message": "Successfully logged out" }`

### `GET /api/v1/auth/me`
Returns current authenticated user profile.
- **Header**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK` &rarr; `UserResponse`

### `GET /api/v1/auth/audit-logs`
Returns security audit trail (Admin & Registrar only).
- **Header**: `Authorization: Bearer <access_token>`
- **Response**: `200 OK` &rarr; `[ { "id": int, "action": "LOGIN_SUCCESS", ... } ]`

---

## 2. Document & Verification Pipeline

### `POST /api/documents/upload`
Uploads deed document or selects pre-calibrated demo preset.
- **Body (Multipart)**: `file: UploadFile?`, `preset_type: string? ('genuine' | 'tampered' | 'collision')`
- **Response**: `200 OK` &rarr; `{ "document_id": int, "verification_id": string, "file_name": string, "file_hash": string }`

### `POST /api/verification/start/{document_id}`
Executes multi-vector forensic verification pipeline.
- **Response**: `200 OK` &rarr; `VerificationReport` (confidence score, spatial collisions, tamper alerts, ZK commitment)

### `GET /api/verification/{verification_id}`
Retrieves existing forensic verification report.

---

## 3. Cadastral & Public Verification

### `GET /api/gis/cadastral-layer`
Returns GeoJSON FeatureCollection of cadastral reference plots.

### `GET /api/public/verify/{document_hash}`
Public trust ledger check without authentication.
