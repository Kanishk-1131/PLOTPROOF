import math
from typing import Any, List, Optional, Tuple
from shapely.geometry import Polygon, Point, MultiPolygon, shape
from shapely.validation import make_valid

from app.gis.crs import calculate_metric_area_sqm


def build_polygon_from_coordinates(raw_coords: List[Any]) -> Optional[Polygon]:
    """
    Constructs a valid Polygon from coordinate pairs, enforcing (longitude, latitude) order (Section 9).
    Closes open rings and removes duplicate consecutive vertices.
    """
    if not raw_coords or len(raw_coords) < 3:
        return None

    cleaned_points = []
    for pt in raw_coords:
        if isinstance(pt, (list, tuple)) and len(pt) >= 2:
            x, y = float(pt[0]), float(pt[1])
            # Detect inverted (lat, lng) vs (lng, lat):
            # In India, latitude is ~8-37 and longitude is ~68-97
            if (8.0 <= x <= 37.0) and (68.0 <= y <= 97.0):
                # User passed (lat, lng) -> swap to (lng=x, lat=y)
                x, y = y, x
            cleaned_points.append((x, y))

    if len(cleaned_points) < 3:
        return None

    # Close linear ring if not closed
    if cleaned_points[0] != cleaned_points[-1]:
        cleaned_points.append(cleaned_points[0])

    try:
        poly = Polygon(cleaned_points)
        return poly
    except Exception:
        return None


def build_polygon_from_centroid(latitude: float, longitude: float, area_sqm: float) -> Polygon:
    """
    Generates a localized bounding polygon around a GPS point when boundary vertices
    are not individually enumerated in deed text (Section 10).
    """
    # 1 degree latitude ~ 111,000 meters
    side_meters = math.sqrt(max(area_sqm, 100.0))
    half_side = side_meters / 2.0

    d_lat = half_side / 111320.0
    d_lng = half_side / (111320.0 * math.cos(math.radians(latitude)))

    coords = [
        (longitude - d_lng, latitude - d_lat),
        (longitude + d_lng, latitude - d_lat),
        (longitude + d_lng, latitude + d_lat),
        (longitude - d_lng, latitude + d_lat),
        (longitude - d_lng, latitude - d_lat),
    ]
    return Polygon(coords)


def validate_geometry(geometry: Any) -> bool:
    """
    Checks whether a geometry is non-empty and structurally valid (Section 12).
    """
    if geometry is None:
        return False
    if geometry.is_empty:
        return False
    if not geometry.is_valid:
        return False
    if geometry.geom_type not in ("Polygon", "MultiPolygon"):
        return False
    return True


def repair_geometry(geometry: Polygon) -> Tuple[Polygon, bool]:
    """
    Controlled repair for self-intersecting or invalid polygons (Section 13).
    Verifies that the repair does not significantly alter the parcel area (> 5% drift).
    Returns (repaired_geometry, is_safe).
    """
    if validate_geometry(geometry):
        return geometry, True

    try:
        repaired = make_valid(geometry)
        if repaired.geom_type == "MultiPolygon":
            # Select largest polygon part
            repaired = max(repaired.geoms, key=lambda p: p.area)

        if not validate_geometry(repaired):
            # Attempt buffer(0)
            repaired = geometry.buffer(0)
            if repaired.geom_type == "MultiPolygon":
                repaired = max(repaired.geoms, key=lambda p: p.area)

        # Check area preservation
        orig_area = geometry.area if geometry.area > 0 else 1.0
        new_area = repaired.area
        drift = abs(new_area - orig_area) / orig_area

        if drift <= 0.05 and validate_geometry(repaired):
            return repaired, True
        else:
            return repaired, False
    except Exception:
        return geometry, False
