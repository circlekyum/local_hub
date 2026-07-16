from contextlib import asynccontextmanager
from typing import Annotated
import logging
import os

from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import create_tables, get_db
from app.routers import posts, places, chat
from app.models import Post  # noqa: F401


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Vibe Backend",
    lifespan=lifespan,
)


# Render의 CORS_ORIGINS 환경 변수를 쉼표 기준으로 분리
raw_cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173",
)

cors_origins = [
    origin.strip().rstrip("/")
    for origin in raw_cors_origins.split(",")
    if origin.strip()
]

logger.warning("Allowed CORS origins: %s", cors_origins)


app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=[
        "Accept",
        "Content-Type",
        "Authorization",
    ],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    errors = []

    for error in exc.errors():
        field = ".".join(
            str(loc)
            for loc in error.get("loc", [])
        )

        errors.append({
            "field": field,
            "message": error.get("msg"),
            "type": error.get("type"),
        })

    return JSONResponse(
        status_code=422,
        content={
            "detail": "입력값이 올바르지 않습니다.",
            "errors": errors,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    logger.error(
        "Database error: %s %s (%s)",
        request.method,
        request.url.path,
        type(exc).__name__,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "데이터베이스 처리 중 오류가 발생했습니다."
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


DbSession = Annotated[Session, Depends(get_db)]


@app.get("/health/db")
def database_health_check(db: DbSession):
    result = db.execute(text("SELECT 1")).scalar()

    return {
        "status": "ok",
        "database": "connected",
        "result": result,
    }


app.include_router(posts.router)
app.include_router(places.router)
app.include_router(chat.router)