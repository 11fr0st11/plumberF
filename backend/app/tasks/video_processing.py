from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import JobVideo


def process_job_video(job_video_id: int):
    """
    Simple background task for now:
    - Mark job as 'processed'
    - Later we'll add: ASR, lesson creation, etc.
    """
    db: Session = SessionLocal()
    try:
        job_video = db.query(JobVideo).filter(JobVideo.id == job_video_id).first()
        if not job_video:
            return

        # Here you could later add: call Whisper, save transcript, etc.
        job_video.status = "processed"
        db.add(job_video)
        db.commit()
    finally:
        db.close()