import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./community.db")
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")


settings = Settings()
