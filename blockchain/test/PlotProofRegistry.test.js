const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("PlotProofRegistry Smart Contract (Layer 8)", function () {
    let registry;
    let owner;
    let unauthorizedUser;

    const sampleVerifId = ethers.keccak256(ethers.toUtf8Bytes("PP-2026-000052"));
    const sampleVerifHash = ethers.keccak256(ethers.toUtf8Bytes("VERIFICATION_HASH_ROOT_123456"));
    const sampleCommitment = ethers.keccak256(ethers.toUtf8Bytes("POSEIDON_COMMITMENT_789012"));

    beforeEach(async function () {
        [owner, unauthorizedUser] = await ethers.getSigners();
        const PlotProofRegistry = await ethers.getContractFactory("PlotProofRegistry");
        registry = await PlotProofRegistry.deploy(owner.address);
        await registry.waitForDeployment();
    });

    it("Test 1: Successful Anchor - Emits VerificationAnchored event and stores record", async function () {
        const tx = await registry.anchorVerification(sampleVerifId, sampleVerifHash, sampleCommitment);
        const receipt = await tx.wait();

        expect(receipt.status).to.equal(1);

        const record = await registry.getVerification(sampleVerifId);
        expect(record.exists).to.be.true;
        expect(record.verificationHash).to.equal(sampleVerifHash);
        expect(record.commitment).to.equal(sampleCommitment);
        expect(record.timestamp).to.be.greaterThan(0);
    });

    it("Test 2: Duplicate Protection - Rejects anchoring same verification ID twice", async function () {
        await registry.anchorVerification(sampleVerifId, sampleVerifHash, sampleCommitment);

        await expect(
            registry.anchorVerification(sampleVerifId, sampleVerifHash, sampleCommitment)
        ).to.be.revertedWith("Verification already exists");
    });

    it("Test 3: Access Control - Rejects unauthorized non-owner accounts", async function () {
        await expect(
            registry.connect(unauthorizedUser).anchorVerification(sampleVerifId, sampleVerifHash, sampleCommitment)
        ).to.be.revertedWithCustomError(registry, "OwnableUnauthorizedAccount");
    });

    it("Test 4: View Retrieval - Returns exact bytes32 records", async function () {
        await registry.anchorVerification(sampleVerifId, sampleVerifHash, sampleCommitment);

        const [vHash, comm, ts, exists] = await registry.getVerification(sampleVerifId);
        expect(exists).to.be.true;
        expect(vHash).to.equal(sampleVerifHash);
        expect(comm).to.equal(sampleCommitment);
    });

    it("Test 5: Non-existent Record - Returns exists as false", async function () {
        const randomId = ethers.keccak256(ethers.toUtf8Bytes("NON_EXISTENT_ID"));
        const record = await registry.getVerification(randomId);
        expect(record.exists).to.be.false;
        expect(record.timestamp).to.equal(0);
    });

    it("Test 6: Input Validation - Rejects bytes32(0) verificationId or verificationHash", async function () {
        const zeroBytes32 = ethers.ZeroHash;
        await expect(
            registry.anchorVerification(zeroBytes32, sampleVerifHash, sampleCommitment)
        ).to.be.revertedWith("Invalid verificationId");

        await expect(
            registry.anchorVerification(sampleVerifId, zeroBytes32, sampleCommitment)
        ).to.be.revertedWith("Invalid verificationHash");
    });
});
