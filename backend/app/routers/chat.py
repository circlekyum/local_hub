from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db, get_attractions_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import generate_answer

router = APIRouter(prefix="/api", tags=["chat"])


CommunityDb = Annotated[Session, Depends(get_db)]
AttractionsDb = Annotated[Session, Depends(get_attractions_db)]

@router.post("/chat", response_model=ChatResponse, summary="지역정보 챗봇")
def chat_endpoint(chat_data: ChatRequest, community_db: CommunityDb, attractions_db: AttractionsDb):
    question = chat_data.question
    answer = generate_answer(question, community_db, attractions_db)
    return ChatResponse(answer=answer)
