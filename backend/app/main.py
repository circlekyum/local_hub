from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import create_tables, get_db
from app.routers import posts, places, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(title="Vibe Backend", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


DbSession = Annotated[Session, Depends(get_db)]


@app.get("/health/db")
def database_health_check(db: DbSession):
    result = db.execute(text("SELECT 1")).scalar()
    return {"status": "ok", "database": "connected", "result": result}


app.include_router(posts.router)
app.include_router(places.router)
app.include_router(chat.router)
