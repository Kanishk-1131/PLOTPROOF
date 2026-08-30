import os
import shutil
import hashlib
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.deed import Document
from app.schemas.verification import UploadResponse

from app.utils.paths import UPLOAD_DIR

router = APIRouter(prefix="/api/documents", tags=["Document Upload"])

@router.get("/default")
async def get_default_demonstration_document():
    """
    Returns the metadata and text content of the default demonstration deed.
    """
    from app.utils.sample_deeds import SAMPLE_DEEDS_INFO, generate_all_sample_deeds
    generate_all_sample_deeds()
    info = SAMPLE_DEEDS_INFO["default"]
    
    txt_path = os.path.join(UPLOAD_DIR, info["filename_txt"])
    content = ""
    if os.path.exists(txt_path):
        with open(txt_path, "r", encoding="utf-8") as f:
            content = f.read()
            
    return {
        "preset_id": "genuine",
        "name": "Default Demonstration Land Title Deed",
        "description": "Clean Tamil Nadu Title Deed for Survey 142/3A (2,400 sq.ft) with zero boundary collisions and valid cryptographic root.",
        "survey_number": info["survey_number"],
        "village": info["village"],
        "taluk": info["taluk"],
        "district": info["district"],
        "area_sqft": 2400.0,
        "area_display": info["area_sqft"],
        "titleholder": info["purchaser"],
        "gps_bounds": info["gps"],
        "registered_hash": info["registered_hash"],
        "pdf_download_url": f"/static/uploads/{info['filename_pdf']}",
        "txt_download_url": f"/static/uploads/{info['filename_txt']}",
        "raw_text": content,
        "expected_outcome": "VERIFIED (100% Authenticity, Zero Overlap, On-Chain Anchor & QR Certificate)"
    }


@router.get("/samples")
async def get_sample_presets():
    """
    Returns demonstration presets (Genuine Default, Authority Review Required, Tampered Area).
    """
    from app.utils.sample_deeds import SAMPLE_DEEDS_INFO, generate_all_sample_deeds
    generate_all_sample_deeds()
    
    return [
        {
            "id": "genuine",
            "tag": "CASE 1 (DEFAULT)",
            "title": "Genuine Title Deed",
            "survey_number": "142/3A",
            "area": "2,400 sq.ft (222.96 m²)",
            "expected_outcome": "VERIFIED (Passed All Checks & QR Issued)",
            "pdf_url": "/static/uploads/sample_default_deed.pdf",
            "txt_url": "/static/uploads/sample_genuine_142_3A.txt",
            "badge_color": "emerald",
            "status_code": "VERIFIED",
            "reason": "Clean boundaries, zero spatial overlap, valid cryptographic hash."
        },
        {
            "id": "review_required",
            "tag": "CASE 2 (AUTHORITY REVIEW)",
            "title": "Authority Review Required Deed",
            "survey_number": "142/3B",
            "area": "2,400 sq.ft (Overlaps 142/3A)",
            "expected_outcome": "REVIEW_REQUIRED (Sub-Registrar Action Needed)",
            "pdf_url": "/static/uploads/demo_collision_deed.pdf",
            "txt_url": "/static/uploads/sample_collision_142_3B.txt",
            "badge_color": "amber",
            "status_code": "REVIEW_REQUIRED",
            "reason": "17.8 m² Cadastral boundary overlap with Survey 142/3A. Section 34 Registration Act statutory hearing required."
        },
        {
            "id": "tampered",
            "tag": "CASE 3",
            "title": "Tampered Title Deed",
            "survey_number": "142/3A",
            "area": "3,400 sq.ft (Altered Extent)",
            "expected_outcome": "TAMPER_ALERT (SHA-256 Mismatch)",
            "pdf_url": "/static/uploads/demo_tampered_deed.pdf",
            "txt_url": "/static/uploads/sample_tampered_area.txt",
            "badge_color": "purple",
            "status_code": "TAMPER_ALERT",
            "reason": "Claimed area (3,400 sq.ft) does not match canonical hash commitment (2,400 sq.ft)."
        }
    ]


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(None),
    preset_type: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handles deed upload via multipart file or instant demo preset selection.
    If neither file nor preset is supplied, defaults to the official Demonstration Deed (Genuine 142/3A).
    """
    count = db.query(Document).count() + 142
    verification_id = f"PP-2026-{count:05d}"
    
    # Ensure sample deeds exist
    from app.utils.sample_deeds import generate_all_sample_deeds
    generate_all_sample_deeds()

    chosen_preset = preset_type.lower() if preset_type else None
    if chosen_preset in ["default", "demo", "sample"]:
        chosen_preset = "genuine"

    if file:
        display_name = file.filename
        dest_filename = f"{verification_id}_{file.filename}"
        dest_path = os.path.join(UPLOAD_DIR, dest_filename)
        
        content = await file.read()
        with open(dest_path, "wb") as f:
            f.write(content)
            
        file_hash = hashlib.sha256(content).hexdigest()
        file_size = len(content)
        mime_type = file.content_type or "application/pdf"
    else:
        # Default or specified preset
        effective_preset = chosen_preset or "genuine"
        preset_map = {
            "genuine": "sample_genuine_142_3A.txt",
            "tampered": "sample_tampered_area.txt",
            "collision": "sample_collision_142_3B.txt",
            "review_required": "sample_collision_142_3B.txt",
            "review": "sample_collision_142_3B.txt"
        }
        filename = preset_map.get(effective_preset, "sample_genuine_142_3A.txt")
        src_path = os.path.join(UPLOAD_DIR, filename)
        
        if not os.path.exists(src_path):
            from app.seed_data.seed_db import seed_database
            seed_database()

        dest_filename = f"{verification_id}_{filename}"
        dest_path = os.path.join(UPLOAD_DIR, dest_filename)
        shutil.copyfile(src_path, dest_path)
        
        with open(dest_path, "rb") as f:
            file_bytes = f.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_size = len(file_bytes)
        mime_type = "text/plain"
        display_name = f"TitleDeed_{effective_preset.capitalize()}.pdf"

    doc = Document(
        owner_user_id=1,
        verification_id=verification_id,
        file_path=dest_path,
        file_name=display_name,
        storage_key=f"uploads/{verification_id}_{display_name}",
        sha256=file_hash,
        file_size=file_size,
        mime_type=mime_type,
        file_hash=file_hash
    )
    db.add(doc)

    db.commit()
    db.refresh(doc)

    return UploadResponse(
        document_id=doc.id,
        verification_id=doc.verification_id,
        file_name=doc.file_name,
        file_hash=doc.file_hash,
        file_size=doc.file_size,
        preview_url=f"/static/uploads/{dest_filename}"
    )
