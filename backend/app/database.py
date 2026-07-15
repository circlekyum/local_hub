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

if settings.attractions_database_url.startswith("sqlite:///"):
    a_db_path = settings.attractions_database_url[len("sqlite:///") : ]
    Path(a_db_path).parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)

connect_args_attractions = {"check_same_thread": False} if settings.attractions_database_url.startswith("sqlite") else {}
engine_attractions = create_engine(settings.attractions_database_url, connect_args=connect_args_attractions)

SessionLocalAttractions = sessionmaker(bind=engine_attractions, autoflush=False, autocommit=False, expire_on_commit=False)

class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_attractions_db() -> Generator[Session, None, None]:
    db = SessionLocalAttractions()
    try:
        yield db
    finally:
        db.close()

def create_tables() -> None:
    try:
        import app.models.post  # community posts
        import app.models.place  # attractions (uses Place -> attractions table)
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=engine_attractions)
