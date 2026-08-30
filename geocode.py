"""
geocode.py
Turns an address string (as extracted by Person 1's OCR module) into
coordinates, and can build a small fallback polygon around a point when
no proper boundary survey data is available.
"""

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from shapely.geometry import Point
import time

_geolocator = Nominatim(user_agent="land-record-gis-module")


def geocode_address(address: str, retries: int = 3):
    """
    Convert a free-text address into (lat, lon).
    Returns None if the address could not be resolved.
    """
    if not address or not address.strip():
        return None

    for attempt in range(retries):
        try:
            location = _geolocator.geocode(address, timeout=10)
            if location:
                return {"lat": location.latitude, "lon": location.longitude,
                        "resolved_address": location.address}
            return None
        except (GeocoderTimedOut, GeocoderServiceError):
            time.sleep(1)  # brief backoff, Nominatim rate-limits aggressively
    return None


def buffer_point_to_polygon(lat: float, lon: float, radius_meters: float = 15.0):
    """
    When OCR/Person 1 only gives an address (no survey boundary), approximate
    the parcel as a small circular polygon around the geocoded point.
    This is a fallback, not a substitute for real survey coordinates.

    Returns a list of [lon, lat] pairs forming a closed ring (GeoJSON style).
    """
    # crude meters -> degrees conversion (fine for small buffers, not for large areas)
    deg_radius = radius_meters / 111_320.0
    point = Point(lon, lat)
    circle = point.buffer(deg_radius, resolution=16)
    return [[round(x, 7), round(y, 7)] for x, y in circle.exterior.coords]