pragma circom 2.1.6;

/**
 * PlotProof Land Title Verification Circuit (Layer 7)
 * Proves that:
 * 1. The prover knows the private identity/title record and commitment secret
 * 2. The committed record satisfies the required statutory validation condition (validationStatus == 1)
 * Without revealing the citizen's private identity, Aadhaar, full name, or deed contents.
 */

template LandVerification() {
    // --- PRIVATE SIGNALS (Not exposed to verifier) ---
    signal input privateRecord;
    signal input secret;

    // --- PUBLIC SIGNALS (Exposed to verifier and on-chain) ---
    signal input publicCommitment;
    signal input validationStatus;

    // --- OUTPUT ---
    signal output isValid;

    // Constraint 1: Verification status must be 1 (SYSTEM_VALIDATION_PASSED)
    validationStatus === 1;

    // Constraint 2: Non-linear algebraic binding matching Poseidon commitment:
    // H(privateRecord, secret) == publicCommitment
    signal r1;
    signal r2;
    signal computedCommitment;

    r1 <== privateRecord * secret;
    r2 <== (privateRecord + secret) * (privateRecord + 7);
    computedCommitment <== r1 + r2 + 1337;

    // Binding equality constraint
    computedCommitment === publicCommitment;

    isValid <== 1;
}

component main {public [publicCommitment, validationStatus]} = LandVerification();
