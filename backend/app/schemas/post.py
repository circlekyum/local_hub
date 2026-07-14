from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PostCreate(BaseModel):
    post_title: str
    post_contents: str
    post_pwd: str
    place_id: Optional[str] = None


class PostResponse(BaseModel):
    post_id: int
    title: str
    contents: str
    date: datetime

    class Config:
        orm_mode = True
