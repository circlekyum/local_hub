from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import ConfigDict
from pydantic import field_validator


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="게시글 제목")
    content: str = Field(min_length=1, max_length=10000, description="게시글 본문")

    @field_validator("title", "content")
    @classmethod
    def reject_blank_value(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


class PostCreate(BaseModel):
    post_title: str
    post_contents: str
    post_pwd: str
    place_id: str | None = None


    @field_validator("post_title", "post_contents")
    @classmethod
    def reject_blank_value_alt(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("공백만 입력할 수 없습니다.")
        return value


class PostUpdate(BaseModel):
    post_title: str
    post_contents: str
    post_pwd: str


class PostDelete(BaseModel):
    post_pwd: str


class PostDeleteResponse(BaseModel):
    id: int
    message: str

    model_config = ConfigDict(from_attributes=True)


class PostListItem(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostResponse(PostBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostByPlaceKeywordResponse(BaseModel):
    place_id: str | None = None
    posts: list[PostListItem] = []

    model_config = ConfigDict(from_attributes=True)

