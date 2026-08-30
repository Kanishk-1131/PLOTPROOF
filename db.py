"""
db.py
Database connection helper for the GIS + PostGIS module.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

# ---- Configuration ----------------------------------------------------
# Set these as environment variables in production; sensible local defaults below.
DB_CONFIG = {
    "host": os.getenv("PG_HOST", "localhost"),
    "port": os.getenv("PG_PORT", "5432"),
    "dbname": os.getenv("PG_DB", "land_records"),
    "user": os.getenv("PG_USER", "postgres"),
    "password": os.getenv("PG_PASSWORD", "postgres"),
}


@contextmanager
def get_conn():
    """Yield a psycopg2 connection, committing on success and rolling back on error."""
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor():
    """Yield a RealDictCursor (rows come back as dicts) inside a managed connection."""
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
        finally:
            cur.close()


def init_db(schema_path: str = "schema.sql"):
    """Run schema.sql against the configured database. Call once at setup time."""
    with open(schema_path, "r") as f:
        sql = f.read()
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(sql)
        cur.close()
    print("Database schema applied successfully.")


if __name__ == "__main__":
    init_db()