from fastapi import APIRouter

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
def chat_endpoint(payload: dict):
    question = payload.get("chat_question") if isinstance(payload, dict) else None
    # Placeholder response until chat service implemented
    return {"chat_answer": f"Received: {question}"}
