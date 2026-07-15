from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate


def get_posts(db: Session) -> List[Post]:
    stmt = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
    return list(db.scalars(stmt).all())


def get_post(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)

# get_post_keyword : keyword를 포함하는 place_id, place_id 를 가진 post 들을 반환
def get_post_keyword(db: Session, keyword: str) -> tuple[list[str], list[Post]]:
    """
    region.title 에 키워드가 포함되는 attractions 레코드의 contentid들을 찾아,
    community DB의 posts 중 place_id가 해당 contentid인 게시글들을 반환합니다.

    반환: (place_ids, posts)
    - place_ids: contentid 문자열 리스트
    - posts: Post 객체 리스트 (최신순)
    """
    if not keyword:
        return [], []

    # Locate region DB (expected at backend/data/region.db)
    from pathlib import Path
    region_db = Path(__file__).resolve().parents[2] / "data" / "region.db"
    if not region_db.exists():
        # no region DB found
        return [], []

    import sqlite3
    try:
        conn = sqlite3.connect(str(region_db))
        cur = conn.cursor()
        # case-insensitive search for title containing keyword
        cur.execute("SELECT DISTINCT contentid FROM attractions WHERE title LIKE ? COLLATE NOCASE", (f"%{keyword}%",))
        rows = cur.fetchall()
        place_ids = [r[0] for r in rows if r[0]]
    finally:
        try:
            conn.close()
        except Exception:
            pass

    if not place_ids:
        return None, []

    # Use the first matched place_id (single string) as requested
    place_id = place_ids[0]

    # Query community posts whose place_id equals the found contentid
    stmt_posts = select(Post).where(Post.place_id == place_id).order_by(Post.created_at.desc(), Post.id.desc())
    posts = list(db.scalars(stmt_posts).all())

    return place_id, posts


def search_posts(db: Session, keyword: str) -> list[Post]:
    """Search posts by title or content containing the keyword."""
    if not keyword:
        return []

    stmt = select(Post).where(
        (Post.title.contains(keyword)) | (Post.content.contains(keyword))
    ).order_by(Post.created_at.desc(), Post.id.desc())

    return list(db.scalars(stmt).all())


def get_posts_by_place(db: Session, place_id: str) -> list[Post]:
    if not place_id:
        return []

    stmt = select(Post).where(Post.place_id == place_id).order_by(Post.created_at.desc(), Post.id.desc())
    return list(db.scalars(stmt).all())


def create_post(db: Session, post_data: PostCreate) -> Post:
    # post_data uses contract names: post_title, post_contents, post_pwd, place_id
    post = Post(
        title=post_data.post_title,
        content=post_data.post_contents,
        password=post_data.post_pwd,
        place_id=post_data.place_id,
    )

    try:
        db.add(post)
        db.commit()
        db.refresh(post)

    except SQLAlchemyError:
        db.rollback()
        raise

    return post


def verify_password(post: Post, password: str) -> bool:
    return post.password == password


def update_post(db: Session, post: Post, post_data) -> Post:
    # post_data is expected to have post_title and post_contents (contract)
    post.title = post_data.post_title
    post.content = post_data.post_contents

    try:
        db.commit()
        db.refresh(post)

    except SQLAlchemyError:
        db.rollback()
        raise

    return post


def delete_post(db: Session, post: Post) -> None:
    try:
        db.delete(post)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise
