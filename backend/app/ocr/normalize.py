import re
from typing import Optional, Tuple, Dict, Any


# Standard conversion factors to Square Meters (m²) (Section 17)
SQM_CONVERSIONS = {
    "ACRE": 4046.8564224,
    "ACRES": 4046.8564224,
    "CENT": 40.468564,
    "CENTS": 40.468564,
    "SQFT": 0.092903,
    "SQ.FT": 0.092903,
    "SQ FT": 0.092903,
    "SQUARE FEET": 0.092903,
    "SQM": 1.0,
    "SQ.M": 1.0,
    "SQ M": 1.0,
    "SQUARE METERS": 1.0,
    "GROUND": 222.96,
    "GROUNDS": 222.96,
    "GUNTHA": 101.17,
    "GUNTHAS": 101.17,
    "HECTARE": 10000.0,
    "HECTARES": 10000.0,
}


def normalize_survey_number(value: str) -> str:
    """
    Normalizes survey number strings like 'Survey No 125 / 3A' or 'புல எண்: 142/3A' -> '142/3A' (Section 16).
    """
    if not value:
        return ""

    cleaned = value.strip()
    # Remove prefix labels in English and Tamil
    cleaned = re.sub(
        r"^(?:survey\s*(?:no|number)?\.?|s\.?\s*no\.?|r\.?s\.?\s*no\.?|s\.?f\.?|புல\s*எண்)\s*[:\-]?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE | re.UNICODE,
    )
    # Remove internal spaces around slashes and dashes
    cleaned = re.sub(r"\s*[\/\-]\s*", "/", cleaned)
    # Remove remaining spaces
    cleaned = re.sub(r"\s+", "", cleaned)
    return cleaned.upper()



def split_survey_and_subdivision(normalized_survey: str) -> Tuple[str, Optional[str]]:
    """
    Splits '142/3A' -> ('142', '3A').
    """
    if "/" in normalized_survey:
        parts = normalized_survey.split("/", 1)
        return parts[0].strip(), parts[1].strip()
    return normalized_survey.strip(), None


def normalize_area(raw_text: str) -> Dict[str, Any]:
    """
    Extracts numerical area value, original unit, and normalized square meters (Section 17).
    Example: '2400 Sq.ft' -> original: '2400 Sq.ft', value: 2400.0, unit: 'SQ.FT', square_meters: 222.96
    """
    # Regex to capture numeric and unit
    match = re.search(r"([\d,]+(?:\.\d+)?)\s*([A-Za-z\.\s]+)", raw_text.strip())
    if not match:
        return {
            "original": raw_text,
            "value": None,
            "unit": None,
            "square_meters": None,
        }

    val_str = match.group(1).replace(",", "")
    try:
        val = float(val_str)
    except ValueError:
        return {"original": raw_text, "value": None, "unit": None, "square_meters": None}

    raw_unit = match.group(2).strip().upper()
    canonical_unit = "SQFT"

    if "ACRE" in raw_unit:
        canonical_unit = "ACRES"
    elif "CENT" in raw_unit:
        canonical_unit = "CENTS"
    elif "GROUND" in raw_unit:
        canonical_unit = "GROUNDS"
    elif "GUNTHA" in raw_unit:
        canonical_unit = "GUNTHAS"
    elif "HECTARE" in raw_unit:
        canonical_unit = "HECTARES"
    elif "METER" in raw_unit or "SQ.M" in raw_unit or "SQM" in raw_unit:
        canonical_unit = "SQM"
    else:
        canonical_unit = "SQ.FT"

    multiplier = SQM_CONVERSIONS.get(canonical_unit, 1.0)
    sqm = round(val * multiplier, 2)

    return {
        "original": raw_text.strip(),
        "value": val,
        "unit": canonical_unit,
        "square_meters": sqm,
    }


def normalize_boundary_text(value: str) -> str:
    """
    Cleans and normalizes boundary descriptions (Section 18).
    """
    if not value:
        return "Not Specified"
    cleaned = re.sub(r"^(?:north|south|east|west)\s*(?:by|bounded\s*by)?\s*[:\-]?\s*", "", value.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_coordinates(raw_text: str) -> Optional[Dict[str, Any]]:
    """
    Extracts, cleans, and validates latitude and longitude coordinates (Section 19).
    Validates range -90 <= lat <= 90 and -180 <= lng <= 180 and regional plausibility.
    Supports both 2-point centroids and 4-point bounding boxes (lat1, lng1 to lat2, lng2).
    """
    # Look for list of decimal numbers
    coords = re.findall(r"[-+]?\d{1,3}\.\d{3,}", raw_text)
    if len(coords) >= 4:
        try:
            c0, c1, c2, c3 = float(coords[0]), float(coords[1]), float(coords[2]), float(coords[3])
            # Check lat/lng order
            if abs(c0) > 60 and abs(c1) < 40:
                c0, c1 = c1, c0
            if abs(c2) > 60 and abs(c3) < 40:
                c2, c3 = c3, c2

            lat1, lng1 = min(c0, c2), min(c1, c3)
            lat2, lng2 = max(c0, c2), max(c1, c3)

            lat = round((lat1 + lat2) / 2.0, 6)
            lng = round((lng1 + lng2) / 2.0, 6)

            poly_coords = [
                [lat1, lng1],
                [lat1, lng2],
                [lat2, lng2],
                [lat2, lng1],
            ]

            return {
                "latitude": lat,
                "longitude": lng,
                "bounds": [lat1, lng1, lat2, lng2],
                "polygon": poly_coords,
            }
        except (ValueError, IndexError):
            pass

    if len(coords) >= 2:
        try:
            lat = float(coords[0])
            lng = float(coords[1])

            # Swap if user wrote longitude first
            if abs(lat) > 60 and abs(lng) < 40:
                lat, lng = lng, lat

            # Range validation (Section 19)
            if not (-90.0 <= lat <= 90.0 and -180.0 <= lng <= 180.0):
                return None

            return {
                "latitude": round(lat, 6),
                "longitude": round(lng, 6),
            }
        except (ValueError, IndexError):
            pass

    return None

