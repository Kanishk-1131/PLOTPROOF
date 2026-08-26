import os
from pathlib import Path

# backend/app/utils/paths.py
# File location: backend/app/utils/paths.py -> parents[2] is backend directory
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BACKEND_DIR / "static"
UPLOAD_DIR = STATIC_DIR / "uploads"
CERT_DIR = STATIC_DIR / "certificates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
CERT_DIR.mkdir(parents=True, exist_ok=True)
