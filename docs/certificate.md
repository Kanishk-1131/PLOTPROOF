# PlotProof Certificate Generation & Verification Portal

## 1. Certificate Overview
When a land deed achieves `VERIFIED` status, PlotProof generates a cryptographic PDF verification certificate.

```
┌────────────────────────────────────────────────────────┐
│         GOVERNMENT OF TAMIL NADU / PLOTPROOF           │
│         LAND TITLE VERIFICATION CERTIFICATE            │
│                                                        │
│ Certificate Number: PP-CERT-2026-000052                │
│ Verification ID:    PP-2026-000052                     │
│ Date of Issue:      26 August 2026                     │
│ Status:             ACTIVE / VERIFIED                  │
├────────────────────────────────────────────────────────┤
│ PROPERTY DETAILS:                                      │
│ Survey Number: 142/3A                                  │
│ Location:      Selaiyur, Tambaram, Chennai             │
│ Extent:        222.96 Sq.meters (2400 Sq.ft)           │
├────────────────────────────────────────────────────────┤
│ CRYPTOGRAPHIC & BLOCKCHAIN VERIFICATION:               │
│ Verification Hash: b94d27b9934d3e08a52e52d7da7dabfac...│
│ Blockchain TX:     0x7f9a1b2c3d4e5f6a7b8c9d0e1f2a3b4...│
│ Network:           Polygon Amoy Testnet (L2)           │
├────────────────────────────────────────────────────────┤
│  ┌───────┐  Scan QR Code to verify authenticity on the │
│  │ █▀▀▀█ │  official PlotProof Public Portal.          │
│  │ █   █ │                                             │
│  │ ▀▀▀▀▀ │  URL: https://plotproof.gov.in/verify/      │
│  └───────┘       PP-2026-000052                        │
├────────────────────────────────────────────────────────┤
│ LEGAL NOTICE & STATUTORY DISCLAIMER:                   │
│ This certificate confirms the verification results     │
│ produced by the PlotProof system. It does not          │
│ independently constitute a government-issued title     │
│ document or legal title guarantee. Official statutory  │
│ determination of property ownership remains subject to │
│ competent Sub-Registrar and Revenue authorities.       │
└────────────────────────────────────────────────────────┘
```

---

## 2. Public Verification Portal Workflow
1. Verifier (bank officer, buyer, lawyer) scans QR code using any smartphone camera.
2. Directs to `https://plotproof.gov.in/verify/{verification_id}`.
3. Portal displays live on-chain status, cross-checking database against Polygon smart contract.
4. If valid: Displays `✓ VERIFIED`.
5. If revoked: Displays `⚠ CERTIFICATE REVOKED`.
6. If tampered: Displays `✗ HASH MISMATCH / INTEGRITY FAILED`.
