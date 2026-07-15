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
        # Prefer ALLOWED_ORIGINS if provided (BE-11)
        origins = os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGINS", "http://localhost:5173")
        self.cors_origins = origins.split(",")
        self.selected_region = os.getenv("SELECTED_REGION", "대전/충청")
        self.region_data_path = os.getenv("REGION_DATA_PATH", "data/region_data.json")
        # Path to the region attractions sqlite DB (used by post_service.get_post_keyword)
        self.region_db_path = os.getenv("REGION_DB_PATH", "data/region.db")

    @property
    def database_url(self) -> str:
        db_path = Path(self.database_path)
        if not db_path.is_absolute():
            db_path = BASE_DIR / db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{db_path.as_posix()}"

    @property
    def region_data_file(self) -> Path:
        data_path = Path(self.region_data_path)
        if not data_path.is_absolute():
            data_path = BASE_DIR / data_path
        return data_path.resolve()

    @property
    def region_db_file(self) -> Path:
        db_path = Path(self.region_db_path)
        if not db_path.is_absolute():
            db_path = BASE_DIR / db_path
        return db_path.resolve()


settings = Settings()
