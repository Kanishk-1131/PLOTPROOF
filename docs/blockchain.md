# PlotProof Blockchain & Smart Contract Architecture

## 1. Core Principle
The blockchain does **not** store land deeds or citizen PII. It provides an immutable, public cryptographic anchor that enables anyone to verify whether a PlotProof verification record has been altered.

---

## 2. Network Specifications
- **Target Network:** Polygon L2 (Amoy Testnet / Mainnet)
- **Chain ID:** `80002` (Amoy Testnet) / `137` (Polygon Mainnet)
- **Contract Language:** Solidity `0.8.20`
- **Gas Optimization:** Fixed `bytes32` digest packing, events for cheap indexing.

---

## 3. Smart Contract Specification (`LandVerificationRegistry.sol`)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LandVerificationRegistry {
    struct VerificationRecord {
        bytes32 verificationHash;
        bytes32 zkCommitment;
        uint64 timestamp;
        uint32 blockNumber;
        bool isRevoked;
    }

    mapping(bytes32 => VerificationRecord) public verifications;

    event VerificationAnchored(
        bytes32 indexed verificationId,
        bytes32 indexed verificationHash,
        bytes32 zkCommitment,
        uint64 timestamp
    );

    event VerificationRevoked(
        bytes32 indexed verificationId,
        string reason,
        uint64 timestamp
    );

    function anchorVerification(
        bytes32 verificationId,
        bytes32 verificationHash,
        bytes32 zkCommitment
    ) external;

    function verifyRecord(
        bytes32 verificationId,
        bytes32 verificationHash
    ) external view returns (bool isValid, bool isRevoked, uint64 timestamp);

    function revokeVerification(
        bytes32 verificationId,
        string calldata reason
    ) external;
}
```
