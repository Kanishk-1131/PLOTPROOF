from typing import Any, Dict, Tuple
from shapely.geometry import Polygon

from app.gis.crs import calculate_metric_area_sqm, project_to_meters


# Boundary touch tolerance in meters (Section 19)
TOUCH_TOLERANCE_METERS = 0.05


def classify_spatial_relationship(
    candidate_poly: Polygon,
    reference_poly: Polygon,
) -> Tuple[str, float, float]:
    """
    Computes exact intersection area and classifies topological relationship (Section 16 & 17):
    DISJOINT, TOUCHING, OVERLAPPING, WITHIN, CONTAINS, IDENTICAL.
    Returns (relationship_type, overlap_area_sqm, overlap_percentage).
    """
    if not candidate_poly.intersects(reference_poly):
        return "DISJOINT", 0.0, 0.0

    # Calculate accurate metric areas
    # If coordinates are in geographic degree range for India (lng > 60, lat > 5), project to UTM meters
    b_cand = candidate_poly.bounds
    if b_cand[0] > 60.0 and b_cand[1] > 5.0:
        cand_metric = project_to_meters(candidate_poly)
        ref_metric = project_to_meters(reference_poly)
    else:
        cand_metric = candidate_poly
        ref_metric = reference_poly

    cand_area = float(cand_metric.area)
    ref_area = float(ref_metric.area)

    intersection = cand_metric.intersection(ref_metric)
    overlap_area = float(intersection.area) if not intersection.is_empty else 0.0


    # Section 16 & 19: Boundary touching vs real overlap
    # If intersection is a LineString or Point, or area is less than touch tolerance
    if overlap_area < TOUCH_TOLERANCE_METERS:
        if candidate_poly.touches(reference_poly) or overlap_area > 0:
            return "TOUCHING", 0.0, 0.0
        return "DISJOINT", 0.0, 0.0

    # Calculate overlap percentage relative to candidate parcel (Section 18)
    overlap_pct = (overlap_area / cand_area * 100.0) if cand_area > 0 else 0.0
    overlap_pct = round(overlap_pct, 2)
    overlap_area = round(overlap_area, 2)

    # Identical check (>99% overlap and areas match within 1%)
    if overlap_pct >= 99.0 and abs(cand_area - ref_area) / ref_area < 0.01:
        return "IDENTICAL", overlap_area, overlap_pct

    # Within check
    if candidate_poly.within(reference_poly) or overlap_pct >= 99.0:
        return "WITHIN", overlap_area, overlap_pct

    # Contains check
    if candidate_poly.contains(reference_poly):
        return "CONTAINS", overlap_area, overlap_pct

    return "OVERLAPPING", overlap_area, overlap_pct


def validate_area_consistency(deed_area_sqm: float, gis_area_sqm: float) -> Dict[str, Any]:
    """
    Evaluates area mismatch percentage between deed claim and authoritative GIS parcel (Section 20).
    difference_percent = abs(deed_area - gis_area) / gis_area * 100
    <= 1% -> NORMAL
    1 - 5% -> REVIEW
    > 5% -> HIGH_RISK
    """
    if gis_area_sqm <= 0:
        return {
            "deed_area_sqm": deed_area_sqm,
            "gis_area_sqm": gis_area_sqm,
            "difference_sqm": 0.0,
            "difference_percent": 0.0,
            "tier": "NORMAL",
        }

    diff_sqm = round(abs(deed_area_sqm - gis_area_sqm), 2)
    diff_pct = round((diff_sqm / gis_area_sqm) * 100.0, 2)

    if diff_pct <= 1.0:
        tier = "NORMAL"
    elif diff_pct <= 5.0:
        tier = "REVIEW"
    else:
        tier = "HIGH_RISK"

    return {
        "deed_area_sqm": deed_area_sqm,
        "gis_area_sqm": gis_area_sqm,
        "difference_sqm": diff_sqm,
        "difference_percent": diff_pct,
        "tier": tier,
    }
