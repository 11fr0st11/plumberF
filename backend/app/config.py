import os
from pydantic import BaseModel
from dotenv import load_dotenv

# 1) Load variables from .env into the environment
load_dotenv()


class Settings(BaseModel):
    # 2) Read DATABASE_URL from env, with a default fallback
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:#T0g3th3r113@localhost:5432/plumberf_dev"
    )


# 3) Create a single Settings instance to be used across the app
settings = Settings()
