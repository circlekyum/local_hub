from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app import models
from app.models.post import Post
from app.schemas.post import PostCreate
from datetime import datetime

router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", summary="List posts grouped by place")
def list_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).order_by(Post.date_created.desc()).all()
    grouped: dict = {}
    for p in posts:
        grouped.setdefault(p.place_id or "unknown", []).append(
            {"post_id": p.id, "post_title": p.title, "date": p.date_created.isoformat()}
        )
    result = [{"place_id": k, "posts": v} for k, v in grouped.items()]
    return result


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {"post_id": p.id, "title": p.title, "contents": p.contents, "date": p.date_created.isoformat()}


@router.post("", status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        title=payload.post_title,
        contents=payload.post_contents,
        pwd=payload.post_pwd,
        place_id=payload.place_id,
        date_created=datetime.utcnow(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"post_success": True, "post_id": post.id}


@router.put("/{post_id}")
def edit_post(post_id: int, payload: PostCreate, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if p.pwd != payload.post_pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
    p.title = payload.post_title
    p.contents = payload.post_contents
    db.commit()
    return {"edit_success": True}


@router.delete("/{post_id}")
def delete_post(post_id: int, payload: dict, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    pwd = payload.get("post_pwd") if isinstance(payload, dict) else None
    if p.pwd != pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
    db.delete(p)
    db.commit()
    return {"delete_success": True}
