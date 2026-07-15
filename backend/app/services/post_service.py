from typing import List

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.post import Post
from app.schemas.post import PostCreate
from app.config import settings
import logging


def get_posts(db: Session) -> List[Post]:
    stmt = select(Post).order_by(Post.created_at.desc(), Post.id.desc())
    return list(db.scalars(stmt).all())


def get_post(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)

# get_post_keyword : keyword를 포함하는 place_id, place_id 를 가진 post 들을 반환
def get_post_keyword(db: Session, keyword: str) -> tuple[str, dict | None, list[Post]]:
    """
    region.title 에 키워드가 포함되는 attractions 레코드의 contentid들을 찾아,
    community DB의 posts 중 place_id가 해당 contentid인 게시글들을 반환합니다.

    반환: (place_ids, posts)
    - place_ids: contentid 문자열 리스트
    - posts: Post 객체 리스트 (최신순)
    """
    if not keyword:
        return "", None, []

    # Locate region DB via settings
    region_db = settings.region_db_file
    if not region_db.exists():
        logging.getLogger(__name__).warning("Region DB not found at %s", region_db)
        return "", []

    import sqlite3
    conn = None
    place_ids: list[str] = []
    place_row = None
    try:
        conn = sqlite3.connect(str(region_db))
        cur = conn.cursor()
        cur.execute(
            "SELECT DISTINCT contentid, title, addr1, addr2, mapx, mapy FROM attractions WHERE title LIKE ? COLLATE NOCASE",
            (f"%{keyword}%",),
        )
        rows = cur.fetchall()
        # rows may contain multiple; we pick first
        place_ids = [r[0] for r in rows if r and r[0]]
        if rows:
            place_row = rows[0]
    except Exception:
        logging.getLogger(__name__).exception("Error querying region DB %s", region_db)
        return "", []
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

    if not place_ids:
        return "", None, []

    place_id = place_ids[0]

    # build place metadata from place_row if present
    place_info = None
    if place_row:
        # place_row order: contentid, title, addr1, addr2, mapx, mapy
        contentid, title, addr1, addr2, mapx, mapy = place_row
        addr_parts = []
        if addr1:
            addr_parts.append(addr1)
        if addr2:
            addr_parts.append(addr2)
        addr = " ".join(addr_parts) if addr_parts else None
        place_info = {
            "id": contentid,
            "longitude": float(mapx) if mapx is not None else None,
            "latitude": float(mapy) if mapy is not None else None,
            "name": title,
            "addr": addr,
        }

    stmt_posts = select(Post).where(Post.place_id == place_id).order_by(Post.created_at.desc(), Post.id.desc())
    posts = list(db.scalars(stmt_posts).all())

    return place_id, place_info, posts


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
