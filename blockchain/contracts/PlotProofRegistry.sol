// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title PlotProofRegistry
 * @dev High-assurance, tamper-evident cryptographic registry for PlotProof land title verifications (Layer 8).
 * Stores only compact fixed-size cryptographic commitments and hashes (bytes32).
 * Strictly omits citizen PII, raw PDF deeds, and ZK witnesses.
 */
contract PlotProofRegistry is Ownable {

    struct Verification {
        bytes32 verificationHash;
        bytes32 commitment;
        uint64 timestamp;
        bool exists;
    }

    // verificationId (keccak256 hash) => Verification record
    mapping(bytes32 => Verification) private verifications;

    event VerificationAnchored(
        bytes32 indexed verificationId,
        bytes32 indexed verificationHash,
        bytes32 indexed commitment,
        uint64 timestamp
    );

    constructor(address initialOwner)
        Ownable(initialOwner)
    {}

    /**
     * @dev Anchors a cryptographically verified land record on-chain.
     * Accessible exclusively by authorized verifier service.
     */
    function anchorVerification(
        bytes32 verificationId,
        bytes32 verificationHash,
        bytes32 commitment
    ) external onlyOwner {
        require(
            !verifications[verificationId].exists,
            "Verification already exists"
        );
        require(verificationId != bytes32(0), "Invalid verificationId");
        require(verificationHash != bytes32(0), "Invalid verificationHash");

        verifications[verificationId] = Verification({
            verificationHash: verificationHash,
            commitment: commitment,
            timestamp: uint64(block.timestamp),
            exists: true
        });

        emit VerificationAnchored(
            verificationId,
            verificationHash,
            commitment,
            uint64(block.timestamp)
        );
    }

    /**
     * @dev Public view method to retrieve anchored verification parameters for tamper auditing.
     */
    function getVerification(
        bytes32 verificationId
    )
        external
        view
        returns (
            bytes32 verificationHash,
            bytes32 commitment,
            uint64 timestamp,
            bool exists
        )
    {
        Verification memory record = verifications[verificationId];

        return (
            record.verificationHash,
            record.commitment,
            record.timestamp,
            record.exists
        );
    }
}
