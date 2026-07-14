from functools import lru_cache
from pathlib import Path
from typing import List
import os

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()


class Settings:
    openai_api_key: str | None = None
    database_path: str = "data/community.db"
    cors_origins: List[str] = ["http://localhost:5173"]

    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.database_path = os.getenv("DATABASE_PATH", "data/community.db")
        self.cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

    @property
    def database_url(self) -> str:
        db_path = Path(self.database_path)
        if not db_path.is_absolute():
            db_path = BASE_DIR / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path.as_posix()}"


settings = Settings()
