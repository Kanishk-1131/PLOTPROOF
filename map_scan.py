"""
map_scan.py
Handles the case where Person 1's pipeline hands off a *scanned map image*
instead of (or alongside) OCR text fields.

Two-step process:
  1. Georeference: map pixel coordinates -> real-world lon/lat, using at
     least 3 known Ground Control Points (GCPs). These GCPs typically come
     from marks on the map whose real-world coordinates are already known
     (e.g. a survey benchmark, a road junction visible on Google Maps, etc.)
     Person 1 or a human reviewer supplies these GCPs alongside the image.
  2. Vectorize: detect the parcel boundary drawn on the map (usually a bold
     outline) using OpenCV contour detection, then convert that pixel
     contour into a real-world polygon using the georeferencing transform.

If you already have proper coordinates (from OCR or GPS), you don't need
this file at all -- go straight to geocode.py / main.py.
"""

import cv2
import numpy as np
from rasterio.transform import from_gcps
from rasterio.control import GroundControlPoint


def build_transform(gcps: list):
    """
    gcps: list of dicts, each: {"pixel_x": .., "pixel_y": .., "lon": .., "lat": ..}
    Need at least 3 non-collinear points; more (4-6) gives a more accurate fit.
    Returns an affine transform mapping pixel (col,row) -> (lon,lat).
    """
    if len(gcps) < 3:
        raise ValueError("Need at least 3 ground control points to georeference a map scan.")

    rasterio_gcps = [
        GroundControlPoint(row=g["pixel_y"], col=g["pixel_x"], x=g["lon"], y=g["lat"])
        for g in gcps
    ]
    return from_gcps(rasterio_gcps)


def pixel_to_lonlat(transform, px: float, py: float):
    lon, lat = transform * (px, py)
    return lon, lat


def extract_largest_boundary(image_path: str, blur_ksize: int = 5,
                              canny_low: int = 50, canny_high: int = 150):
    """
    Detect the most prominent closed contour in the scanned map -- assumed
    to be the parcel boundary. Returns a list of (pixel_x, pixel_y) points.

    Tune canny_low/canny_high and blur_ksize per scan quality; noisy scans
    need more blur, high-contrast scans can lower the thresholds.
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {image_path}")

    blurred = cv2.GaussianBlur(img, (blur_ksize, blur_ksize), 0)
    edges = cv2.Canny(blurred, canny_low, canny_high)

    # Dilate slightly to close small gaps in hand-drawn/scanned boundary lines
    kernel = np.ones((3, 3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        raise ValueError("No boundary contour detected in the map scan.")

    largest = max(contours, key=cv2.contourArea)

    # Simplify the contour so we don't store thousands of near-duplicate points
    epsilon = 0.002 * cv2.arcLength(largest, True)
    simplified = cv2.approxPolyDP(largest, epsilon, True)

    return [(int(pt[0][0]), int(pt[0][1])) for pt in simplified]


def scanned_map_to_polygon(image_path: str, gcps: list):
    """
    Full pipeline: scanned map image + GCPs -> real-world polygon
    (list of [lon, lat] pairs, ready to insert into PostGIS).
    """
    transform = build_transform(gcps)
    pixel_points = extract_largest_boundary(image_path)

    polygon = [list(pixel_to_lonlat(transform, px, py)) for px, py in pixel_points]

    # Close the ring if not already closed (first point == last point)
    if polygon[0] != polygon[-1]:
        polygon.append(polygon[0])

    return polygon