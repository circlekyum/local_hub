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
