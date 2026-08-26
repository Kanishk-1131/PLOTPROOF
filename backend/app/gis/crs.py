import pyproj
from shapely.geometry import Polygon
from shapely.ops import transform

# Base Geographic CRS (Section 8)
GEOGRAPHIC_CRS = "EPSG:4326"

# State Projected Local Metric CRS for Tamil Nadu & South India (UTM Zone 44N)
PROJECTED_METRIC_CRS = "EPSG:32644"

# Cached Transformer instances (always_xy=True ensures (longitude=x, latitude=y))
_to_metric_transformer = pyproj.Transformer.from_crs(GEOGRAPHIC_CRS, PROJECTED_METRIC_CRS, always_xy=True)
_to_geo_transformer = pyproj.Transformer.from_crs(PROJECTED_METRIC_CRS, GEOGRAPHIC_CRS, always_xy=True)


def project_to_meters(geom_4326: Polygon) -> Polygon:
    """
    Transforms a polygon from EPSG:4326 (degrees) to EPSG:32644 (meters) for accurate spatial math (Section 8).
    """
    return transform(_to_metric_transformer.transform, geom_4326)


def project_to_degrees(geom_metric: Polygon) -> Polygon:
    """
    Transforms a polygon from EPSG:32644 (meters) back to EPSG:4326 (degrees).
    """
    return transform(_to_geo_transformer.transform, geom_metric)


def calculate_metric_area_sqm(geom_4326: Polygon) -> float:
    """
    Computes true geodesic metric area in square meters rather than degree-squared distortion (Section 8).
    """
    if geom_4326.is_empty:
        return 0.0
    projected = project_to_meters(geom_4326)
    return round(float(projected.area), 2)
