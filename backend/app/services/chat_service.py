from typing import List, Optional
import os

from openai import OpenAI
from pydantic import BaseModel
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.post import Post
from app.models.place import Place

_api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")

if not _api_key:
    raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

_client = OpenAI(api_key=_api_key)

# 모듈 레벨 간단한 메모리 스토어 (프로세스 재시작시 사라짐)
SUMMARY_STORE: dict = {}
_GLOBAL_SUMMARY_KEY = "__global__"

def _get_summary(conversation_id: Optional[str]) -> Optional[str]:
    key = conversation_id or _GLOBAL_SUMMARY_KEY
    return SUMMARY_STORE.get(key)

def _set_summary(conversation_id: Optional[str], summary: str) -> None:
    key = conversation_id or _GLOBAL_SUMMARY_KEY
    SUMMARY_STORE[key] = summary

def _summarize_conversation(existing_summary: Optional[str], user_msg: str, bot_msg: str) -> str:
    prompt = (
        f"기존 요약:\n{existing_summary or '없음'}\n\n"
        f"최근 사용자 발화:\n{user_msg}\n\n"
        "위 내용을 반영하여 대화 요약을 간결하게 업데이트하세요. "
        "요약은 사용자의 의도만 포함하고, 100자 이내로 작성하세요."
    )
    resp = _client.responses.create(
        model="gpt-5-mini",
        instructions="대화 요약을 업데이트 하되, 불필요한 문장은 제거하고 핵심만 남기세요.",
        input=prompt,
    )
    return (resp.output_text or "").strip()
class SearchKeywords(BaseModel):
    keywords: List[str]


def _extract_keywords_with_llm(question: str) -> List[str]:
    """
    사용자의 질문에서 DB 검색에 필요한 핵심 키워드를 LLM으로 추출합니다.
    """

    response = _client.responses.parse(
        model="gpt-5-mini",
        instructions=(
            "사용자의 질문에서 지역 커뮤니티 게시글 검색에 필요한 "
            "핵심 명사와 고유명사만 추출하세요.\n"
            "조사와 어미는 제거하세요.\n"
            "'대한', '글', '있다면', '알려줘', '정보'처럼 "
            "검색에 도움이 되지 않는 일반적인 표현은 제외하세요.\n"
            "장소 이름은 원형으로 반환하세요.\n"
            "키워드는 최대 5개까지만 반환하세요."
        ),
        input=question,
        text_format=SearchKeywords,
    )

    parsed = response.output_parsed

    if not parsed:
        return []

    return [
        keyword.strip()
        for keyword in parsed.keywords
        if keyword and keyword.strip()
    ]


def _retrieve_posts_by_keywords(
    db: Session,
    keywords: List[str],
    limit: int = 5,
) -> List[Post]:
    """
    LLM이 추출한 키워드로 게시글 제목과 본문을 검색합니다.
    """

    if not keywords:
        return []

    conditions = []

    for keyword in keywords:
        like = f"%{keyword}%"

        conditions.append(
            or_(
                Post.title.ilike(like),
                Post.content.ilike(like),
            )
        )

    return (
        db.query(Post)
        .filter(or_(*conditions))
        .order_by(Post.created_at.desc())
        .limit(limit)
        .all()
    )

# 신규: attractions 검색
def _retrieve_attractions_by_keywords(
    db: Session,
    keywords: List[str],
    limit: int = 5,
) -> List[Place]:
    if not keywords:
        return []
    conditions = []
    for keyword in keywords:
        like = f"%{keyword}%"
        conditions.append(Place.title.ilike(like))
        conditions.append(Place.raw.ilike(like))
    return db.query(Place).filter(or_(*conditions)).limit(limit).all()

def _build_context_text(posts: List[Post]) -> str:
    if not posts:
        return "관련 문서가 없습니다."

    parts = []

    for index, post in enumerate(posts, start=1):
        title = post.title or ""
        content = (post.content or "")[:2000]

        parts.append(
            f"[문서 {index}]\n"
            f"제목: {title}\n"
            f"내용: {content}"
        )

    return "\n\n---\n\n".join(parts)

def generate_answer(
    question: str,
    community_db: Session,
    attractions_db: Session,
    conversation_id: Optional[str] = None,
) -> str:
    question = question.strip()
    if not question:
        return "질문을 입력해주세요."

    # 이전 요약 불러오기
    existing_summary = _get_summary(conversation_id)

    keywords = _extract_keywords_with_llm(question)

    posts = _retrieve_posts_by_keywords(db=community_db, keywords=keywords, limit=10)
    attractions = _retrieve_attractions_by_keywords(db=attractions_db, keywords=keywords, limit=20)

    # context 병합 (기존 코드 재사용)
    context_parts = []
    if posts:
        context_parts.append(_build_context_text(posts))
    if attractions:
        parts = []
        for idx, a in enumerate(attractions, start=1):
            parts.append(
                f"[관광지 {idx}]\n"
                f"제목: {a.title or ''}\n"
                f"주소: {a.addr1 or ''}\n"
                f"요약: {(a.raw or '')[:2000]}"
            )
        context_parts.append("\n\n---\n\n".join(parts))

    context = "\n\n---\n\n".join(context_parts) if context_parts else "관련 문서가 없습니다."

    # LLM 호출 시 기존 요약을 포함
    response = _client.responses.create(
        model="gpt-5-mini",
        instructions=(
            "당신은 지역 커뮤니티 도움봇입니다.\n"
            "제공된 문서에 근거해서 명확하고 간결하게 답하세요.\n"
            "문서의 내용을 그대로 출력하지 말고, 문서의 내용을 바탕으로 사용자의 질문에 맞게 요약해서 답하세요.\n"
            "문서에 없는 내용은 추정하지 마세요.\n"
            "관련 문서가 없다면 관련 정보를 찾지 못했다고 답하세요.\n"
            "문장마다 들여쓰기를 하세요."
        ),
        input=(
            f"대화 요약:\n{existing_summary or '없음'}\n\n"
            f"사용자 질문:\n{question}\n\n"
            f"검색 키워드:\n{', '.join(keywords)}\n\n"
            f"참고 문서:\n{context}"
        ),
    )

    answer = response.output_text
    if not answer:
        return "답변을 생성하지 못했습니다."

    answer = answer.strip()

    # 답변 생성 후 요약 업데이트
    try:
        new_summary = _summarize_conversation(existing_summary, question, answer)
        if new_summary:
            _set_summary(conversation_id, new_summary)
    except Exception:
        # 요약 실패시에도 답변은 반환하도록 예외 무시
        pass

    return answer