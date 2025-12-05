from fastapi import FastAPI

from .routers import job_videos

app = FastAPI(title="Plumber F API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


# Include routers
app.include_router(job_videos.router)
