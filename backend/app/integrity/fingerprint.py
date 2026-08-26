import hashlib
from typing import Any, Dict, List, Optional

from app.integrity.canonical import canonical_json
from app.integrity.hashing import sha256_bytes


def compute_metadata_hash(fields: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 fingerprint of structured statutory metadata (Section 8).
    Fields typically contain: survey_number, district, taluk, village, area_sq_m, boundaries, etc.
    """
    # Clean fields: sort and omit internal DB keys like id, document_id, created_at
    cleaned: Dict[str, Any] = {}
    for k, v in fields.items():
        if k in ("id", "document_id", "created_at", "updated_at"):
            continue
        cleaned[k] = v

    canonical_bytes = canonical_json(cleaned)
    return sha256_bytes(canonical_bytes)


def compute_ocr_hash(raw_text: str, blocks: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Computes a deterministic SHA-256 fingerprint for OCR output text and layout bounding blocks.
    """
    payload: Dict[str, Any] = {
        "raw_text": (raw_text or "").strip(),
        "block_count": len(blocks) if blocks else 0,
    }
    if blocks:
        # Include first 100 block representations deterministically
        sample_blocks = []
        for b in blocks[:100]:
            sample_blocks.append({
                "text": b.get("text", ""),
                "confidence": round(float(b.get("confidence", 0.0)), 3),
                "page": b.get("page", 1),
            })
        payload["blocks"] = sample_blocks

    return sha256_bytes(canonical_json(payload))


def compute_spatial_hash(spatial_data: Dict[str, Any]) -> str:
    """
    Computes a deterministic SHA-256 fingerprint for Layer 5 GIS validation output.
    """
    cleaned = {
        "geometry_valid": bool(spatial_data.get("geometry_valid", True)),
        "spatial_relationship": str(spatial_data.get("spatial_relationship", "DISJOINT")),
        "overlap_area_sq_m": round(float(spatial_data.get("overlap_area_sq_m", 0.0)), 2),
        "overlap_percentage": round(float(spatial_data.get("overlap_percentage", 0.0)), 2),
        "area_difference_percent": round(float(spatial_data.get("area_difference_percent", 0.0)), 2),
        "survey_number": str(spatial_data.get("survey_number", "")),
        "crs": str(spatial_data.get("crs", "EPSG:4326")),
    }
    return sha256_bytes(canonical_json(cleaned))


def create_verification_hash(
    document_hash: str,
    ocr_hash: str,
    metadata_hash: str,
    spatial_hash: str,
) -> str:
    """
    Builds the composite cryptographic verification hash linking all stages (Section 12):
    Document Hash + OCR Hash + Metadata Hash + Spatial Hash -> Verification Hash.
    """
    payload = {
        "document_hash": document_hash,
        "ocr_hash": ocr_hash,
        "metadata_hash": metadata_hash,
        "spatial_hash": spatial_hash,
    }
    return sha256_bytes(canonical_json(payload))
