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
from app.schemas import ErrorResponse
from app.services import post_service
from typing import Annotated

router = APIRouter(prefix="/api/posts", tags=["posts"])


DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[PostListItem], summary="게시글 목록 조회")
def list_posts(db: DbSession):
    posts = post_service.get_posts(db)
    return posts


@router.get("/search", response_model=list[PostListItem], summary="게시글 제목/본문 검색")
def search_posts(keyword: str, db: DbSession):
    posts = post_service.search_posts(db, keyword)
    return posts


@router.get("/by_place/{place_id}", response_model=list[PostListItem], summary="특정 장소의 게시글 조회")
def posts_by_place(place_id: str, db: DbSession):
    posts = post_service.get_posts_by_place(db, place_id)
    return posts


@router.get("/by_place_keyword", summary="place_id 키워드로 place_id 목록과 관련 게시글 반환")
def posts_by_place_keyword(keyword: str, db: DbSession):
    try:
        place_id, place_info, posts = post_service.get_post_keyword(db, keyword)
    except Exception:
        # unexpected error when querying region DB or posts
        raise HTTPException(status_code=500, detail="지역 검색 처리 중 오류가 발생했습니다.")

    # normalize empty place_id to None for client clarity
    if not place_id:
        return {"place_id": None, "place": None, "posts": []}

    return {
        "place_id": place_id,
        "place": place_info,
        "posts": [PostListItem.from_orm(p) for p in posts],
    }


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="게시글 상세 조회",
    responses={404: {"model": ErrorResponse, "description": "게시글 없음"}},
)
def get_post(post_id: int, db: DbSession):
    # centralized 404 handling
    post = post_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="게시글을 찾을 수 없습니다.")
    return post


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="게시글 작성",
    responses={500: {"model": ErrorResponse, "description": "DB 처리 실패"}},
)
def create_post(post_data: PostCreate, db: DbSession):
    try:
        post = post_service.create_post(db, post_data)
        return post
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="게시글 저장 중 오류가 발생했습니다.")


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    summary="게시글 수정",
    responses={
        403: {"model": ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": ErrorResponse, "description": "게시글 없음"},
        500: {"model": ErrorResponse, "description": "DB 처리 실패"},
    },
)
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

@router.delete(
    "/{post_id}",
    response_model=PostDeleteResponse,
    summary="게시글 삭제",
    responses={
        403: {"model": ErrorResponse, "description": "비밀번호 불일치"},
        404: {"model": ErrorResponse, "description": "게시글 없음"},
        500: {"model": ErrorResponse, "description": "DB 처리 실패"},
    },
)
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
