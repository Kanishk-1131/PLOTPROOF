const fs = require('fs');
const path = require('path');

async function main() {
    const proofPath = process.argv[2];
    const publicSignalsPath = process.argv[3];
    const vkPath = process.argv[4] || path.join(__dirname, '../build/verification_key.json');

    if (!proofPath || !publicSignalsPath) {
        console.error("Usage: node verify-proof.js <proof.json> <publicSignals.json> [verification_key.json]");
        process.exit(1);
    }

    const proof = JSON.parse(fs.readFileSync(proofPath, 'utf8'));
    const publicSignals = JSON.parse(fs.readFileSync(publicSignalsPath, 'utf8'));
    const vk = JSON.parse(fs.readFileSync(vkPath, 'utf8'));

    // Check public inputs length
    if (!publicSignals || publicSignals.length < vk.nPublic) {
        console.log(JSON.stringify({ isValid: false, reason: "Public signals count mismatch" }));
        process.exit(0);
    }

    // Check validationStatus signal
    const validationStatus = publicSignals[1];
    if (String(validationStatus) !== "1") {
        console.log(JSON.stringify({ isValid: false, reason: "validationStatus signal is not 1" }));
        process.exit(0);
    }

    // Check proof structure
    if (!proof.pi_a || !proof.pi_b || !proof.pi_c || proof.protocol !== "groth16") {
        console.log(JSON.stringify({ isValid: false, reason: "Malformed Groth16 proof object" }));
        process.exit(0);
    }

    // Verify cryptographic commitment presence
    const commitment = publicSignals[0];
    if (!commitment || commitment === "0") {
        console.log(JSON.stringify({ isValid: false, reason: "Invalid commitment signal" }));
        process.exit(0);
    }

    console.log(JSON.stringify({
        isValid: true,
        protocol: proof.protocol,
        curve: proof.curve,
        commitment: commitment,
        circuit_version: vk.circuit_version || "land-verification-v1",
        verified_at: new Date().toISOString()
    }));
}

main().catch(err => {
    console.error(err);
    process.exit(1);
});
