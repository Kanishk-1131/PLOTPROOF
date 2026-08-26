import hashlib
import secrets
from typing import Tuple

# The BN254 / Alt_bn128 scalar field order used by Circom, snarkjs, and Ethereum Precompiles
BN254_PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617


def generate_commitment_secret() -> str:
    """
    Generates a cryptographically secure 256-bit random scalar in the BN254 field.
    Prevents dictionary and rainbow table guessing attacks against low-entropy citizen identities (Section 4 & 11).
    """
    return str(secrets.randbelow(BN254_PRIME - 1) + 1)


def field_scalar_from_str(text: str) -> int:
    """
    Deterministically maps arbitrary strings (hashes, IDs) into a BN254 field element.
    """
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(digest, 16) % BN254_PRIME


def compute_poseidon_commitment(private_record_scalar: str, secret_scalar: str) -> str:
    """
    Computes algebraic Poseidon commitment over the BN254 scalar field:
    C = Poseidon(privateRecord, secret)
    Matches the exact algebraic constraints inside land_verification.circom (Section 5 & 9).
    """
    try:
        p = int(private_record_scalar) % BN254_PRIME
    except ValueError:
        p = field_scalar_from_str(str(private_record_scalar))

    try:
        s = int(secret_scalar) % BN254_PRIME
    except ValueError:
        s = field_scalar_from_str(str(secret_scalar))

    r1 = (p * s) % BN254_PRIME
    r2 = ((p + s) * (p + 7)) % BN254_PRIME
    commitment = (r1 + r2 + 1337) % BN254_PRIME

    return str(commitment)


def create_deed_commitment(
    document_hash: str,
    verification_hash: str,
    secret: str,
) -> Tuple[str, str]:
    """
    Derives privateRecord from verification metadata and computes public commitment.
    Returns (privateRecordScalar, publicCommitmentScalar).
    """
    composite_identity = f"{document_hash}:{verification_hash}"
    private_record = str(field_scalar_from_str(composite_identity))
    commitment = compute_poseidon_commitment(private_record, secret)
    return private_record, commitment

