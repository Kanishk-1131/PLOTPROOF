# PlotProof Cryptographic Integrity & Hash Chain

## 1. Core Principle
Cryptographic hashing does not prove legal validity; it proves that the exact digital bytes and structured data verified by PlotProof have remained unmodified.

---

## 2. Canonical Serialization (RFC 8785)
To prevent hash divergence due to key ordering or whitespace differences, all JSON payloads are serialized according to **RFC 8785 (JSON Canonicalization Scheme)**:
- Deterministic lexicographical sorting of dictionary keys
- Removal of arbitrary whitespace
- Uniform floating-point number formatting

---

## 3. Multi-Stage Verification Hash Chain

```
[Raw File Bytes] ──► SHA-256 ──► H_file
[OCR Output]     ──► RFC 8785 ──► SHA-256 ──► H_ocr
[Metadata]       ──► RFC 8785 ──► SHA-256 ──► H_meta
[Spatial Geoms]  ──► RFC 8785 ──► SHA-256 ──► H_spatial

H_verification = SHA-256(H_file || H_ocr || H_meta || H_spatial)
```

**Consequence:** Any modification to a single character in the deed, a single digit in the survey number, or a single coordinate in the GIS geometry alters `H_verification` and invalidates the cryptographic verification chain.
