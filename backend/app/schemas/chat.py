from pydantic import BaseModel, Field
from pydantic import field_validator


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500, description="사용자 질문")

    @field_validator("question")
    @classmethod
    def reject_blank_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("질문을 입력해주세요.")
        return value


class ChatResponse(BaseModel):
    answer: str
