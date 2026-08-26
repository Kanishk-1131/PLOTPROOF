// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title PlotProofRegistry
 * @dev Immutable on-chain registry for land deed verification records & cryptographic SHA-256 fingerprints.
 * No citizen PII or raw deeds are stored on-chain.
 */
contract PlotProofRegistry {
    
    struct LandRecord {
        bytes32 documentHash;
        string verificationId;
        string surveyNumber;
        uint256 registeredTimestamp;
        bool isVerified;
        address registrar;
    }

    // Mapping from document SHA-256 hash to verification record
    mapping(bytes32 => LandRecord) public records;
    
    // Mapping from verification ID to document hash
    mapping(string => bytes32) public verificationIdToHash;

    event DocumentRegistered(
        bytes32 indexed documentHash,
        string indexed verificationId,
        string surveyNumber,
        uint256 timestamp,
        address indexed registrar
    );

    event DocumentRevoked(
        bytes32 indexed documentHash,
        string reason,
        uint256 timestamp
    );

    address public admin;

    modifier onlyAdmin() {
        require(msg.sender == admin, "PlotProof: Only admin can execute");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    /**
     * @notice Registers a verified land deed record on the blockchain.
     * @param _documentHash SHA-256 hash of the canonical land deed data.
     * @param _verificationId Unique PlotProof verification identifier (e.g. PP-2026-00142).
     * @param _surveyNumber Cadastral survey number (e.g. 142/3A).
     */
    function registerDocument(
        bytes32 _documentHash,
        string calldata _verificationId,
        string calldata _surveyNumber
    ) external {
        require(records[_documentHash].registeredTimestamp == 0, "PlotProof: Record already registered");

        records[_documentHash] = LandRecord({
            documentHash: _documentHash,
            verificationId: _verificationId,
            surveyNumber: _surveyNumber,
            registeredTimestamp: block.timestamp,
            isVerified: true,
            registrar: msg.sender
        });

        verificationIdToHash[_verificationId] = _documentHash;

        emit DocumentRegistered(
            _documentHash,
            _verificationId,
            _surveyNumber,
            block.timestamp,
            msg.sender
        );
    }

    /**
     * @notice Verifies whether a document hash is validly registered on-chain.
     * @param _documentHash The SHA-256 hash to verify.
     */
    function verifyDocument(bytes32 _documentHash) external view returns (
        bool isRegistered,
        string memory verificationId,
        string memory surveyNumber,
        uint256 registeredTimestamp,
        bool isVerified
    ) {
        LandRecord memory rec = records[_documentHash];
        if (rec.registeredTimestamp == 0) {
            return (false, "", "", 0, false);
        }
        return (true, rec.verificationId, rec.surveyNumber, rec.registeredTimestamp, rec.isVerified);
    }
}
