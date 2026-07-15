from typing import List
import os
import re
from openai import OpenAI
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.post import Post

_api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
_client = OpenAI(api_key=_api_key)


def _retrieve_posts_by_keywords(db: Session, question: str, limit: int = 5) -> List[Post]:
    tokens = [t for t in re.findall(r'[\uac00-\ud7a3a-zA-Z0-9]+', question) if len(t) > 1]
    if not tokens:
        q = f"%{question}%"
        return (
            db.query(Post)
            .filter(or_(Post.title.ilike(q), Post.content.ilike(q)))
            .order_by(Post.created_at.desc())
            .limit(limit)
            .all()
        )

    conds = []
    for t in tokens:
        like = f"%{t}%"
        conds.append(or_(Post.title.ilike(like), Post.content.ilike(like)))

    return (
        db.query(Post)
        .filter(or_(*conds))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )


def _build_context_text(posts: List[Post]) -> str:
    parts = []
    for p in posts:
        parts.append(f"제목: {p.title}\n내용: {p.content}\n---")
    return "\n".join(parts) if parts else "관련 문서가 없습니다."


def generate_answer(question: str, db: Session) -> str:
    docs = _retrieve_posts_by_keywords(db, question, limit=5)
    context = _build_context_text(docs)

    system_prompt = (
        "당신은 지역 커뮤니티 도움봇입니다. 아래 문서들을 참고해서 명확하고 간결하게 답해주세요. "
        "문서에 없는 정보는 추정하지 마시고 모른다고 답하세요.\n\n문서:\n" + context
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    resp = _client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
    )
    return resp.choices[0].message.content.strip()