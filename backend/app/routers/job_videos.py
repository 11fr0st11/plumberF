from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import JobVideo, Trade
from app.schemas import (
    JobVideoCreate,
    JobVideoRead,
    JobVideoInitiateRequest,
    JobVideoInitiateResponse,
    JobVideoConfirmUploadRequest,
)
from app.tasks.video_processing import process_job_video


router = APIRouter(
    prefix="/job-videos",
    tags=["job-videos"],
)

@router.post("/initiate", response_model=JobVideoInitiateResponse)
def initiate_job_video_upload(
    payload: JobVideoInitiateRequest,
    db: Session = Depends(get_db),
):
    # 1) Ensure trade exists
    trade = db.query(Trade).filter(Trade.id == payload.trade_id).first()
    if not trade:
        raise HTTPException(status_code=400, detail="Invalid trade_id")

    # 2) TEMP: assume uploader_id = 1 until we implement auth
    uploader_id = 1

    # 3) Create JobVideo with status "upload_pending"
    job_video = JobVideo(
        uploader_id=uploader_id,
        trade_id=payload.trade_id,
        job_type_free_text=payload.job_type_free_text,
        location_type=payload.location_type,
        difficulty_level=payload.difficulty_level,
        file_url="",  # we don't know yet; will be set on confirm
        status="upload_pending",
        original_filename=f"pending_upload.{payload.file_extension}",
    )

    db.add(job_video)
    db.commit()
    db.refresh(job_video)

    # 4) For now, generate a fake local upload URL
    # Later this becomes a presigned S3/MinIO URL.
    upload_url = f"local-dev://upload/job_videos/{job_video.id}.{payload.file_extension}"

    return JobVideoInitiateResponse(
        job_video_id=job_video.id,
        upload_url=upload_url,
    )


@router.post("/{job_video_id}/confirm-upload", response_model=JobVideoRead)
def confirm_job_video_upload(
    job_video_id: int,
    payload: JobVideoConfirmUploadRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    job_video = db.query(JobVideo).filter(JobVideo.id == job_video_id).first()
    if not job_video:
        raise HTTPException(status_code=404, detail="Job video not found")

    # Update file_url and mark as uploaded
    job_video.file_url = payload.file_url
    job_video.status = "uploaded"

    db.add(job_video)
    db.commit()
    db.refresh(job_video)

    # 🔹 Schedule background processing (no Redis, just FastAPI)
    background_tasks.add_task(process_job_video, job_video.id)

    return job_video


@router.post("/", response_model=JobVideoRead)
def create_job_video(payload: JobVideoCreate, db: Session = Depends(get_db)):
    # 1) Ensure trade exists
    trade = db.query(Trade).filter(Trade.id == payload.trade_id).first()
    if not trade:
        raise HTTPException(status_code=400, detail="Invalid trade_id")

    # 2) TEMP: assume uploader_id = 1 until auth is implemented
    uploader_id = 1

    # 3) Create JobVideo row
    job_video = JobVideo(
        uploader_id=uploader_id,
        trade_id=payload.trade_id,
        job_type_free_text=payload.job_type_free_text,
        location_type=payload.location_type,
        difficulty_level=payload.difficulty_level,
        file_url=payload.file_url or "",  # placeholder for now
        status="uploaded",
    )

    db.add(job_video)
    db.commit()
    db.refresh(job_video)

    return job_video


@router.get("/{job_video_id}", response_model=JobVideoRead)
def get_job_video(job_video_id: int, db: Session = Depends(get_db)):
    job_video = db.query(JobVideo).filter(JobVideo.id == job_video_id).first()
    if not job_video:
        raise HTTPException(status_code=404, detail="Job video not found")
    return job_video