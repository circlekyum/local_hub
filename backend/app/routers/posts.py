from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal
from app import models
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate, PostDelete
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
    posts = db.query(Post).order_by(Post.created_at.desc()).all()
    grouped: dict = {}
    for p in posts:
        key = p.place_id or "default"
        grouped.setdefault(key, []).append(
            {"post_id": p.id, "post_title": p.title, "date": p.created_at.isoformat()}
        )
    result = [{"place_id": k, "posts": v} for k, v in grouped.items()]
    return result


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return {
        "post_id": p.id,
        "title": p.title,
        "contents": p.content,
        "date": p.created_at.isoformat(),
    }


@router.post("", status_code=201)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    post = Post(
        title=payload.post_title,
        content=payload.post_contents,
        password=payload.post_pwd,
        place_id=payload.place_id,
        created_at=datetime.utcnow(),
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {"post_success": True, "post_id": post.id}


@router.put("/{post_id}")
def edit_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if p.password != payload.post_pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
    p.title = payload.post_title
    p.content = payload.post_contents
    db.commit()
    return {"edit_success": True}


@router.delete("/{post_id}")
def delete_post(post_id: int, payload: PostDelete, db: Session = Depends(get_db)):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if p.password != payload.post_pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
    db.delete(p)
    db.commit()
    return {"delete_success": True}
