from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api", tags=["chat"])


DbSession = Annotated[Session, Depends(get_db)]


@router.post("/chat", response_model=ChatResponse, summary="지역정보 챗봇")
def chat_endpoint(chat_data: ChatRequest, db: DbSession):
    # Placeholder: team3 should implement chat_service.generate_answer
    # This uses DB session so chat service can query posts.
    question = chat_data.question
    return ChatResponse(answer=f"임시 응답: {question}")
