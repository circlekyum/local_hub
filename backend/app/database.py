from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# Ensure data directory exists when using a relative SQLite path
if settings.database_url.startswith("sqlite:///"):
    # Extract path after 'sqlite:///' (keeps relative paths like ./data/community.db)
    db_path = settings.database_url[len("sqlite:///") :]
    path = Path(db_path)
    # Create parent directories for the DB file when path is relative or absolute
    Path(path.parent).mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    # Import models to ensure they are registered with Base metadata
    try:
        import app.models.post  # noqa: F401
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
