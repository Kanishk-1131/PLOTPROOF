from datetime import datetime
from pydantic import BaseModel


class ProcessingJobSummary(BaseModel):
    job_type: str
    status: str
    attempts: int
    error_message: str | None = None


class DocumentResponse(BaseModel):
    id: int
    owner_user_id: int
    file_name: str
    mime_type: str
    file_size: int
    storage_key: str
    sha256: str
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    download_url: str | None = None
    is_duplicate: bool = False

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    document_id: int
    file_name: str
    file_size: int
    mime_type: str
    sha256: str
    status: str
    version: int
    is_duplicate: bool
    download_url: str
    created_at: datetime


class DocumentStatusResponse(BaseModel):
    document_id: int
    file_name: str
    status: str
    sha256: str
    version: int
    processing: ProcessingJobSummary | None = None


class DocumentDownloadResponse(BaseModel):
    document_id: int
    file_name: str
    download_url: str
    expires_in_seconds: int = 900
