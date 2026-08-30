-- ============================================================
-- schema.sql
-- PostGIS schema for the GIS + PostGIS module (Person 2)
-- ============================================================

-- Enable PostGIS extension (run once per database)
CREATE EXTENSION IF NOT EXISTS postgis;

-- Main table storing land parcels / records
CREATE TABLE IF NOT EXISTS parcels (
    id             SERIAL PRIMARY KEY,
    survey_no      VARCHAR(100),
    owner_name     VARCHAR(255),
    address        TEXT,
    source         VARCHAR(50) DEFAULT 'ocr',      -- 'ocr', 'manual', 'map_scan'
    geom           GEOMETRY(Polygon, 4326),         -- parcel boundary (lon/lat, WGS84)
    centroid       GEOMETRY(Point, 4326),           -- auto-derived center point
    is_flagged     BOOLEAN DEFAULT FALSE,           -- true if overlap/duplicate suspected
    created_at     TIMESTAMP DEFAULT NOW(),
    updated_at     TIMESTAMP DEFAULT NOW()
);

-- Spatial index -- critical for fast overlap / point-in-polygon queries
CREATE INDEX IF NOT EXISTS idx_parcels_geom ON parcels USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_parcels_centroid ON parcels USING GIST (centroid);

-- Auto-update centroid + updated_at whenever geom changes
CREATE OR REPLACE FUNCTION update_parcel_derived_fields()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.geom IS NOT NULL THEN
        NEW.centroid := ST_Centroid(NEW.geom);
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_parcel_derived_fields ON parcels;
CREATE TRIGGER trg_parcel_derived_fields
BEFORE INSERT OR UPDATE ON parcels
FOR EACH ROW EXECUTE FUNCTION update_parcel_derived_fields();

-- Table logging overlap/duplicate checks (useful evidence for Person 3's trust layer)
CREATE TABLE IF NOT EXISTS parcel_conflicts (
    id            SERIAL PRIMARY KEY,
    parcel_id     INTEGER REFERENCES parcels(id) ON DELETE CASCADE,
    conflict_with INTEGER REFERENCES parcels(id) ON DELETE CASCADE,
    overlap_pct   NUMERIC,          -- % of parcel_id's area that overlaps conflict_with
    detected_at   TIMESTAMP DEFAULT NOW()
);