from fastapi import FastAPI
from .config import settings

app = FastAPI(title="Plumber F API")


@app.get("/health")
def health_check():
    return {
        "status": "ok",
    }
