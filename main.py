"""
main.py
FastAPI service for Person 2: GIS + PostGIS module.

Pipeline position:  Person 1 (AI + OCR)  --->  [THIS SERVICE]  --->  Person 3 (Backend + Trust)

Run locally:
    uvicorn main:app --reload --port 8002

Endpoints:
    POST /parcels/ingest        -> accepts OCR/scan output, stores + validates a parcel
    GET  /parcels/{id}          -> fetch one parcel as GeoJSON
    GET  /parcels/check-point   -> which parcel (if any) contains a given lat/lon
    GET  /parcels/{id}/overlaps -> list parcels overlapping this one
    GET  /parcels/conflicts     -> full list of flagged conflicts (for Person 3's trust layer)
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import json
from decimal import Decimal

from db import get_cursor
from geocode import geocode_address, buffer_point_to_polygon
from map_scan import scanned_map_to_polygon

app = FastAPI(title="Land Record GIS Module", version="1.0")


# ---------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------

class GCP(BaseModel):
    pixel_x: float
    pixel_y: float
    lon: float
    lat: float


class ParcelIngestRequest(BaseModel):
    # Fields handed off from Person 1's OCR step
    survey_no: Optional[str] = None
    owner_name: Optional[str] = None
    address: Optional[str] = None

    # Option A: already-known boundary coordinates, e.g. [[lon,lat], [lon,lat], ...]
    polygon: Optional[List[List[float]]] = None

    # Option B: only an address was OCR'd -> we geocode + buffer a fallback polygon
    # (nothing extra needed, `address` above is used)

    # Option C: a scanned map image was supplied instead of clean text/coords
    map_image_path: Optional[str] = None
    gcps: Optional[List[GCP]] = None


class PointCheckResult(BaseModel):
    found: bool
    parcel_id: Optional[int] = None
    survey_no: Optional[str] = None
    owner_name: Optional[str] = None


# ---------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------

def _polygon_to_wkt(polygon: List[List[float]]) -> str:
    """Convert [[lon,lat], ...] into WKT POLYGON string for PostGIS."""
    if polygon[0] != polygon[-1]:
        polygon = polygon + [polygon[0]]
    coord_str = ", ".join(f"{lon} {lat}" for lon, lat in polygon)
    return f"POLYGON(({coord_str}))"


def _detect_conflicts(cur, parcel_id: int):
    """
    Check the newly inserted parcel against all others for overlap.
    Flags the parcel and logs conflicts if overlap % exceeds a threshold.
    This is the signal Person 3's trust/fraud layer consumes.
    """
    cur.execute(
        """
        SELECT p2.id,
               ST_Area(ST_Intersection(p1.geom, p2.geom)::geography)
                 / NULLIF(ST_Area(p1.geom::geography), 0) * 100 AS overlap_pct
        FROM parcels p1
        JOIN parcels p2 ON p1.id != p2.id
        WHERE p1.id = %s
          AND ST_Intersects(p1.geom, p2.geom)
        """,
        (parcel_id,),
    )
    conflicts = cur.fetchall()

    for c in conflicts:
        if c["overlap_pct"] and c["overlap_pct"] > 5:  # >5% overlap = suspicious
            cur.execute(
                """INSERT INTO parcel_conflicts (parcel_id, conflict_with, overlap_pct)
                   VALUES (%s, %s, %s)""",
                (parcel_id, c["id"], c["overlap_pct"]),
            )
            cur.execute("UPDATE parcels SET is_flagged = TRUE WHERE id IN (%s, %s)",
                        (parcel_id, c["id"]))

    return [c for c in conflicts if c["overlap_pct"] and c["overlap_pct"] > 5]


def _sanitize_row(row):
    """Convert psycopg2 RealDictRow to a plain dict with JSON-safe types."""
    import datetime
    clean = {}
    for k, v in row.items():
        if isinstance(v, Decimal):
            clean[k] = float(v)
        elif isinstance(v, (datetime.datetime, datetime.date)):
            clean[k] = v.isoformat()
        else:
            clean[k] = v
    return clean


def _sanitize_rows(rows):
    """Sanitize a list of RealDictRow results."""
    return [_sanitize_row(r) for r in rows]


# ---------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------

@app.post("/parcels/ingest")
def ingest_parcel(req: ParcelIngestRequest):
    """
    Single entry point Person 1 (or Person 3 relaying Person 1's output) calls.
    Handles all three input scenarios: clean polygon, address-only, or map scan.
    """
    polygon = req.polygon
    source = "ocr"

    # Scenario C: scanned map image + GCPs
    if polygon is None and req.map_image_path and req.gcps:
        gcps = [g.model_dump() for g in req.gcps]
        polygon = scanned_map_to_polygon(req.map_image_path, gcps)
        source = "map_scan"

    # Scenario B: address only -> geocode + buffer
    if polygon is None and req.address:
        geo = geocode_address(req.address)
        if not geo:
            raise HTTPException(422, f"Could not geocode address: {req.address}")
        polygon = buffer_point_to_polygon(geo["lat"], geo["lon"])
        source = "geocoded_address"

    if polygon is None:
        raise HTTPException(
            422,
            "Provide one of: `polygon` (survey coords), `address` (to geocode), "
            "or `map_image_path` + `gcps` (scanned map).",
        )

    wkt = _polygon_to_wkt(polygon)

    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO parcels (survey_no, owner_name, address, source, geom)
            VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            RETURNING id
            """,
            (req.survey_no, req.owner_name, req.address, source, wkt),
        )
        new_id = cur.fetchone()["id"]

        conflicts = _detect_conflicts(cur, new_id)

    return {
        "parcel_id": new_id,
        "source": source,
        "flagged": len(conflicts) > 0,
        "conflicts": _sanitize_rows(conflicts),
        "message": "Parcel stored. Overlaps detected -- review before certification."
        if conflicts else "Parcel stored with no boundary conflicts.",
    }


# --- Fixed-path routes MUST come before /parcels/{parcel_id} ---


@app.get("/parcels/check-point", response_model=PointCheckResult)
def check_point(lat: float = Query(...), lon: float = Query(...)):
    """Given a coordinate (e.g. from a field GPS reading), find which parcel contains it."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, survey_no, owner_name
            FROM parcels
            WHERE ST_Contains(geom, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            LIMIT 1
            """,
            (lon, lat),
        )
        row = cur.fetchone()

    if not row:
        return PointCheckResult(found=False)

    return PointCheckResult(found=True, parcel_id=row["id"],
                             survey_no=row["survey_no"], owner_name=row["owner_name"])


@app.get("/parcels/conflicts")
def list_conflicts():
    """All flagged conflicts -- this is what Person 3's trust layer should poll/consume."""
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT pc.id, pc.parcel_id, pc.conflict_with, pc.overlap_pct, pc.detected_at,
                   p1.owner_name AS parcel_owner, p2.owner_name AS conflict_owner
            FROM parcel_conflicts pc
            JOIN parcels p1 ON pc.parcel_id = p1.id
            JOIN parcels p2 ON pc.conflict_with = p2.id
            ORDER BY pc.detected_at DESC
            """
        )
        rows = cur.fetchall()
    return {"conflicts": _sanitize_rows(rows)}


# --- Parameterized routes below ---


@app.get("/parcels/{parcel_id}")
def get_parcel(parcel_id: int):
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT id, survey_no, owner_name, address, source, is_flagged,
                   created_at, ST_AsGeoJSON(geom) AS geojson
            FROM parcels WHERE id = %s
            """,
            (parcel_id,),
        )
        row = cur.fetchone()

    if not row:
        raise HTTPException(404, "Parcel not found")

    row = _sanitize_row(row)
    row["geometry"] = json.loads(row.pop("geojson"))
    return row


@app.get("/parcels/{parcel_id}/overlaps")
def get_overlaps(parcel_id: int):
    with get_cursor() as cur:
        cur.execute(
            """
            SELECT p2.id, p2.survey_no, p2.owner_name,
                   ST_Area(ST_Intersection(p1.geom, p2.geom)::geography) AS overlap_area_sqm
            FROM parcels p1
            JOIN parcels p2 ON p1.id != p2.id
            WHERE p1.id = %s AND ST_Intersects(p1.geom, p2.geom)
            """,
            (parcel_id,),
        )
        overlaps = cur.fetchall()
    return {"parcel_id": parcel_id, "overlaps": _sanitize_rows(overlaps)}


@app.get("/health")
def health():
    return {"status": "ok"}