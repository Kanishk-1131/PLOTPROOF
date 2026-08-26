# PlotProof Zero-Knowledge Privacy System

## 1. Objective
Prove that a land verification satisfies state registry conditions without exposing citizen personal identifiable information (PII) on-chain or to third parties.

---

## 2. Cryptographic Parameters
- **Prime Curve:** BN254 / Alt_bn128 ($r = 21888242871839275222246405745257275088548364400416034343698204186575808495617$)
- **Proof System:** Groth16 zk-SNARK
- **Hash Function:** Poseidon Algebraic Hash over $\mathbb{F}_r$

---

## 3. Private vs Public Inputs

| Privacy Classification | Data Elements | Destination |
|:---|:---|:---|
| **Private Witness (Secret)** | Citizen Name, Aadhaar UID, Phone, Secret Blinding Scalar ($s$), Raw Deed Bytes | Kept strictly inside citizen/server isolated memory; never written to DB or chain. |
| **Public Commitments** | $C = \text{Poseidon}(\text{DeedScalar}, s)$, Verification Hash ($H_v$) | Stored in PlotProof database and anchored to Polygon smart contract. |
| **Zero-Knowledge Proof** | $\pi = (A \in \mathbb{G}_1, B \in \mathbb{G}_2, C \in \mathbb{G}_1)$ | Verified on-chain or via local Snarkjs gate before anchoring. |

---

## 4. Circuit Logic (`land_verification.circom`)
1. Proves ownership of secret scalar $s$ satisfying $C = \text{Poseidon}(\text{DeedScalar}, s)$.
2. Proves verification status meets statutory thresholds (integrity passed, no boundary collision).
3. Zero-Knowledge guarantee: Verifier learns only that the proof is valid, without learning citizen identity.
