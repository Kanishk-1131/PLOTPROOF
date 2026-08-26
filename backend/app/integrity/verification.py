from enum import Enum
from typing import Any, Dict

from app.integrity.hashing import sha256_bytes


class VerificationState(str, Enum):
    PROCESSING = "PROCESSING"
    INTEGRITY_CHECKED = "INTEGRITY_CHECKED"
    GIS_VALIDATED = "GIS_VALIDATED"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    APPROVED = "APPROVED"
    ANCHORED = "ANCHORED"
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
    SPATIAL_RISK = "SPATIAL_RISK"
    FRAUD_SUSPECTED = "FRAUD_SUSPECTED"
    INVALID = "INVALID"


def verify_file_integrity(stored_hash: str, presented_bytes: bytes) -> Dict[str, Any]:
    """
    Compares the digital fingerprint of an uploaded/presented document against
    the immutable stored hash (Section 18).
    Never claims to verify legal validity; only verifies byte-for-byte fidelity.
    """
    computed_hash = sha256_bytes(presented_bytes)
    is_match = stored_hash.strip().lower() == computed_hash.strip().lower()

    return {
        "integrity": "MATCH" if is_match else "MISMATCH",
        "stored_hash": stored_hash,
        "computed_hash": computed_hash,
        "is_valid": is_match,
    }


def classify_verification_outcome(
    integrity_pass: bool,
    spatial_pass: bool,
    ocr_acceptable: bool,
    ocr_confidence: float = 1.0,
) -> Dict[str, Any]:
    """
    Distinguishes independent failure signals rather than collapsing into generic fraud (Section 21 & 22):
    - Cryptographic tampering -> INTEGRITY_FAILURE
    - Spatial collision / overlap -> SPATIAL_RISK
    - Low OCR confidence / ambiguous text -> REVIEW_REQUIRED
    - Clear pass -> SYSTEM_VALIDATION_PASSED
    """
    if not integrity_pass:
        return {
            "status": VerificationState.INTEGRITY_FAILURE.value,
            "decision": "INTEGRITY_FAILURE",
            "anomaly_type": "CRYPTOGRAPHIC_TAMPERING",
            "message": "File byte hash does not match the originally registered record.",
            "approvable": False,
        }

    if not spatial_pass:
        return {
            "status": VerificationState.SPATIAL_RISK.value,
            "decision": "SPATIAL_COLLISION",
            "anomaly_type": "SPATIAL_ANOMALY",
            "message": "Topological overlap or boundary collision detected against cadastral registry.",
            "approvable": False,
        }

    if not ocr_acceptable or ocr_confidence < 0.70:
        return {
            "status": VerificationState.REVIEW_REQUIRED.value,
            "decision": "REVIEW_REQUIRED",
            "anomaly_type": "OCR_ANOMALY",
            "message": "Low OCR extraction confidence or statutory field ambiguity requires human review.",
            "approvable": False,
        }

    return {
        "status": VerificationState.APPROVED.value,
        "decision": "SYSTEM_VALIDATION_PASSED",
        "anomaly_type": "NONE",
        "message": "Cryptographic integrity, GIS topology, and OCR statutory fields successfully validated.",
        "approvable": True,
    }
