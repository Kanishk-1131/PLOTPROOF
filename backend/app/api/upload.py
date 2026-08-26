import os
import shutil
import hashlib
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.deed import Document
from app.schemas.verification import DocumentUploadResponse

from app.utils.paths import UPLOAD_DIR

router = APIRouter(prefix="/api/documents", tags=["Document Upload"])

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(None),
    preset_type: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Handles deed upload via multipart file or instant demo preset selection:
    - preset_type: 'genuine', 'tampered', 'collision'
    """
    count = db.query(Document).count() + 142
    verification_id = f"PP-2026-{count:05d}"
    
    if preset_type:
        preset_map = {
            "genuine": "sample_genuine_142_3A.txt",
            "tampered": "sample_tampered_area.txt",
            "collision": "sample_collision_142_3B.txt"
        }
        filename = preset_map.get(preset_type.lower(), "sample_genuine_142_3A.txt")
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
        display_name = f"TitleDeed_{preset_type.capitalize()}.pdf"
    elif file:
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
        raise HTTPException(status_code=400, detail="Either file or preset_type must be provided")

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

    return DocumentUploadResponse(
        document_id=doc.id,
        verification_id=doc.verification_id,
        file_name=doc.file_name,
        file_hash=doc.file_hash,
        file_size=doc.file_size,
        preview_url=f"/static/uploads/{dest_filename}"
    )
