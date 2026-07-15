import sqlite3
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services.post_service import get_post_keyword
from app.models.post import Post
from app.database import Base
from app.config import settings


def test_get_post_keyword_matches_posts(tmp_path):
    # Create a temporary region DB with an attractions table
    region_db_path = tmp_path / "region.db"
    conn = sqlite3.connect(str(region_db_path))
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE attractions (contentid TEXT PRIMARY KEY, title TEXT)"
    )
    # insert a matching attraction
    cur.execute(
        "INSERT INTO attractions (contentid, title) VALUES (?, ?)",
        ("place123", "Some Keyword Place"),
    )
    conn.commit()
    conn.close()

    # Override settings to point to this region DB
    settings.region_db_path = str(region_db_path)

    # Create an in-memory SQLite for posts and create the tables
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Add a Post whose place_id matches the region contentid
    p = Post(title="Test", content="Body", password="pwd", place_id="place123")
    session.add(p)
    session.commit()

    # Call the function under test
    place_id, posts = get_post_keyword(session, "Keyword")

    assert place_id == "place123"
    assert isinstance(posts, list)
    assert len(posts) == 1
    assert posts[0].place_id == "place123"
