from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.database.session import get_db
from app.models.document import Document
from app.models.processing_job import ProcessingJob
from app.models.user import User
from app.schemas.document import (
    DocumentDownloadResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
    ProcessingJobSummary,
)
from app.services.document_service import DocumentService
from app.services.storage_service import StorageService

router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Document Ingestion & Secure Storage"],
)

doc_service = DocumentService()
storage_service = StorageService()


@router.post(
    "",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(

    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else None
    document, job, is_duplicate = doc_service.ingest_document(
        db=db,
        user=current_user,
        upload_file=file,
        ip_address=client_ip,
    )

    download_url = storage_service.generate_presigned_url(document.storage_key)

    return DocumentUploadResponse(
        document_id=document.id,
        file_name=document.file_name,
        file_size=document.file_size,
        mime_type=document.mime_type,
        sha256=document.sha256,
        status=document.status.value,
        version=document.version,
        is_duplicate=is_duplicate,
        download_url=download_url,
        created_at=document.created_at,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = doc_service.list_documents_for_user(db=db, user=current_user, limit=limit)
    res = []
    for d in docs:
        d_dict = DocumentResponse(
            id=d.id,
            owner_user_id=d.owner_user_id,
            file_name=d.file_name,
            mime_type=d.mime_type,
            file_size=d.file_size,
            storage_key=d.storage_key,
            sha256=d.sha256,
            status=d.status.value,
            version=d.version,
            created_at=d.created_at,
            updated_at=d.updated_at,
            download_url=storage_service.generate_presigned_url(d.storage_key),
            is_duplicate=False,
        )
        res.append(d_dict)
    return res


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    return DocumentResponse(
        id=doc.id,
        owner_user_id=doc.owner_user_id,
        file_name=doc.file_name,
        mime_type=doc.mime_type,
        file_size=doc.file_size,
        storage_key=doc.storage_key,
        sha256=doc.sha256,
        status=doc.status.value,
        version=doc.version,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        download_url=storage_service.generate_presigned_url(doc.storage_key),
    )


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
)
def get_document_status(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)

    # Get latest processing job
    job = db.scalar(
        select(ProcessingJob)
        .where(ProcessingJob.document_id == doc.id)
        .order_by(desc(ProcessingJob.created_at))
    )

    job_summary = None
    if job:
        job_summary = ProcessingJobSummary(
            job_type=job.job_type,
            status=job.status.value,
            attempts=job.attempts,
            error_message=job.error_message,
        )

    return DocumentStatusResponse(
        document_id=doc.id,
        file_name=doc.file_name,
        status=doc.status.value,
        sha256=doc.sha256,
        version=doc.version,
        processing=job_summary,
    )


@router.get(
    "/{document_id}/download",
    response_model=DocumentDownloadResponse,
)
def get_document_download(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = doc_service.get_document_with_auth(db=db, document_id=document_id, user=current_user)
    signed_url = storage_service.generate_presigned_url(doc.storage_key, expiration=900)

    return DocumentDownloadResponse(
        document_id=doc.id,
        file_name=doc.file_name,
        download_url=signed_url,
        expires_in_seconds=900,
    )


@router.get(
    "/raw/{storage_key:path}",
    include_in_schema=False,
)
def stream_raw_document(
    storage_key: str,
    db: Session = Depends(get_db),
):
    # Lookup document
    doc = db.scalar(select(Document).where(Document.storage_key == storage_key))
    if not doc:
        raise HTTPException(status_code=404, detail="File not found")

    local_path = storage_service.get_local_path(storage_key)
    if not local_path or not local_path.exists():
        raise HTTPException(status_code=404, detail="Storage object not available")

    return FileResponse(
        path=local_path,
        media_type=doc.mime_type,
        filename=doc.file_name,
    )


@router.delete(
    "/{document_id}",
)
def delete_document(
    document_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    client_ip = request.client.host if request.client else None
    doc_service.delete_document(
        db=db,
        document_id=document_id,
        user=current_user,
        ip_address=client_ip,
    )
    return {"message": f"Document {document_id} deleted successfully"}
