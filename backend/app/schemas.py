from typing import Optional
from pydantic import BaseModel


# ---------- JobVideo ----------

class JobVideoBase(BaseModel):
    trade_id: int
    job_type_free_text: Optional[str] = None
    location_type: Optional[str] = None
    difficulty_level: Optional[int] = None
    file_url: Optional[str] = None  # we will make this real later


class JobVideoCreate(JobVideoBase):
    """Payload for creating a new JobVideo."""
    # For now, uploader_id is assumed (e.g. 1) until we add auth.


class JobVideoRead(JobVideoBase):
    id: int
    uploader_id: int
    status: str

    class Config:
        orm_mode = True


class JobVideoInitiateRequest(BaseModel):
    trade_id: int
    job_type_free_text: Optional[str] = None
    location_type: Optional[str] = None
    difficulty_level: Optional[int] = None
    file_extension: str  # e.g. "mp4", "mov"


class JobVideoInitiateResponse(BaseModel):
    job_video_id: int
    upload_url: str

    class Config:
        orm_mode = True


class JobVideoConfirmUploadRequest(BaseModel):
    file_url: str  # final location of the uploaded file