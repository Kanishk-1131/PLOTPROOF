from typing import Any, Dict


def calculate_spatial_risk_score(
    geometry_valid: bool,
    geometry_repaired: bool,
    spatial_relationship: str,
    overlap_percentage: float,
    area_difference_percent: float,
    coordinate_confidence: float,
    parcel_matched: bool,
) -> Dict[str, Any]:
    """
    Computes an explicit multi-factor spatial risk score (0-100) (Section 21):
    - Geometry Validity (20%)
    - Overlap Severity (35%)
    - Area Mismatch (20%)
    - Coordinate Confidence (10%)
    - Parcel Identification (15%)
    """
    # 1. Geometry factor (20%)
    if not geometry_valid:
        geom_risk = 20.0
    elif geometry_repaired:
        geom_risk = 10.0
    else:
        geom_risk = 0.0

    # 2. Overlap factor (35%)
    if spatial_relationship in ("DISJOINT", "TOUCHING", "IDENTICAL"):
        overlap_risk = 0.0
    elif spatial_relationship == "WITHIN":
        overlap_risk = 5.0
    else:  # OVERLAPPING or CONTAINS
        if overlap_percentage <= 2.0:
            overlap_risk = 10.0
        elif overlap_percentage <= 10.0:
            overlap_risk = 20.0
        elif overlap_percentage <= 30.0:
            overlap_risk = 30.0
        else:
            overlap_risk = 35.0

    # 3. Area mismatch factor (20%)
    if area_difference_percent <= 1.0:
        area_risk = 0.0
    elif area_difference_percent <= 5.0:
        area_risk = 10.0
    else:
        area_risk = 20.0

    # 4. Coordinate confidence factor (10%)
    if coordinate_confidence >= 0.90:
        coord_risk = 0.0
    elif coordinate_confidence >= 0.70:
        coord_risk = 5.0
    else:
        coord_risk = 10.0

    # 5. Parcel identification factor (15%)
    if parcel_matched:
        id_risk = 0.0
    else:
        id_risk = 15.0

    total_score = round(geom_risk + overlap_risk + area_risk + coord_risk + id_risk, 1)

    # Classify Risk Level (Section 21)
    if spatial_relationship == "OVERLAPPING":
        risk_level = "HIGH" if total_score < 75.0 else "CRITICAL"
        decision = "SPATIAL_COLLISION"
    elif total_score <= 20.0:
        risk_level = "LOW"
        decision = "CLEAR"
    elif total_score <= 50.0:
        risk_level = "MEDIUM"
        decision = "REVIEW_REQUIRED"
    elif total_score <= 75.0:
        risk_level = "HIGH"
        decision = "REVIEW_REQUIRED"
    else:
        risk_level = "CRITICAL"
        decision = "FLAGGED"


    return {
        "score": total_score,
        "level": risk_level,
        "decision": decision,
        "breakdown": {
            "geometry_risk": geom_risk,
            "overlap_risk": overlap_risk,
            "area_risk": area_risk,
            "coordinate_risk": coord_risk,
            "identification_risk": id_risk,
        },
    }
