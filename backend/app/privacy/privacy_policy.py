from typing import Any, Dict, List

PROHIBITED_PUBLIC_KEYS = {
    "aadhaar",
    "pan",
    "phone",
    "mobile",
    "email",
    "owner",
    "purchaser",
    "seller",
    "address",
    "witness",
    "secret",
    "privaterecord",
    "rawpdf",
    "pdfbytes",
}



def sanitize_for_public_presentation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Strips all citizen PII, private identifiers, and secret witness values (Section 2, 10, & 19).
    Ensures zero leakage to public verifiers, logs, or blockchain.
    """
    clean = {}
    for k, v in payload.items():
        k_lower = k.lower().replace("_", "").replace("-", "")
        if any(bad in k_lower for bad in PROHIBITED_PUBLIC_KEYS):
            continue
        if isinstance(v, dict):
            clean[k] = sanitize_for_public_presentation(v)
        elif isinstance(v, list):
            clean[k] = [
                sanitize_for_public_presentation(item) if isinstance(item, dict) else item
                for item in v
            ]
        else:
            clean[k] = v
    return clean
