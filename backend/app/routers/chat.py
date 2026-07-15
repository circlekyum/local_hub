from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_answer

router = APIRouter(prefix="/api", tags=["chat"])


DbSession = Annotated[Session, Depends(get_db)]



@router.post("/chat", response_model=ChatResponse, summary="지역정보 챗봇")
def chat_endpoint(chat_data: ChatRequest, db: DbSession):
    question = chat_data.question
    answer = generate_answer(question, db)
    return ChatResponse(answer=answer)
