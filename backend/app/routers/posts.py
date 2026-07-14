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


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED, summary="게시글 작성")
def create_post(post_data: PostCreate, db: DbSession):
    try:
        post = post_service.create_post(db, post_data)
        return post
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="게시글 저장 중 오류가 발생했습니다.")


@router.put("/{post_id}", response_model=PostResponse, summary="게시글 수정")
def edit_post(post_id: int, payload: PostUpdate, db: DbSession):
    post = post_service.get_post(db, post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    if not post_service.verify_password(post, payload.post_pwd):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 일치하지 않습니다.")

    try:
        updated = post_service.update_post(db, post, payload)
        return updated
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="게시글 수정 중 오류가 발생했습니다.")


from app.schemas import PostDeleteResponse

@router.delete("/{post_id}", response_model=PostDeleteResponse, summary="게시글 삭제")
def delete_post(post_id: int, payload: PostDelete, db: DbSession):
    post = post_service.get_post(db, post_id)

    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")

    if not post_service.verify_password(post, payload.post_pwd):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="비밀번호가 일치하지 않습니다.")

    try:
        post_service.delete_post(db, post)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="게시글 삭제 중 오류가 발생했습니다.")

    return PostDeleteResponse(id=post_id, message="게시글이 삭제되었습니다.")
