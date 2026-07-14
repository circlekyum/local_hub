from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, get_db
from app import models
from app.models.post import Post
from app.schemas.post import (
    PostCreate,
    PostListItem,
    PostResponse,
    PostUpdate,
    PostDelete,
)
from app.services import post_service
from typing import Annotated

router = APIRouter(prefix="/api/posts", tags=["posts"])


DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[PostListItem], summary="게시글 목록 조회")
def list_posts(db: DbSession):
    posts = post_service.get_posts(db)
    return posts


@router.get("/{post_id}", response_model=PostResponse, summary="게시글 상세 조회")
def get_post(post_id: int, db: DbSession):
    p = post_service.get_post(db, post_id)
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    return p


@router.post("", status_code=201)
@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
)
def create_post(post_data: PostCreate, db: DbSession):
    try:
        post = post_service.create_post(db, post_data)
        return post
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="게시글 저장 중 오류가 발생했습니다.")


@router.put("/{post_id}")
@router.put("/{post_id}")
def edit_post(post_id: int, payload: PostUpdate, db: DbSession):
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
@router.delete("/{post_id}")
def delete_post(post_id: int, payload: PostDelete, db: DbSession):
    p = db.query(Post).filter(Post.id == post_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if p.password != payload.post_pwd:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong password")
    db.delete(p)
    db.commit()
    return {"delete_success": True}
