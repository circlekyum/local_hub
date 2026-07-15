# API 계약서 (버전 1)

다음은 FE와 BE가 합의한 게시글·장소·챗봇 API 명세입니다.

## 공통 오류 형식
- 응답 JSON 기본 형태:

```json
{ "success": false, "detail": "오류 설명" }
```

- HTTP 상태 코드 요약:
  - 200: 정상 처리
  - 201: 생성 성공
  - 400: 잘못된 요청
  - 403: 비밀번호 불일치(권한 없음)
  - 404: 리소스 없음
  - 422: 유효성 검사 실패

---

## 게시글 목록 조회
- Method: `GET`
- Endpoint: `/api/posts`
- 설명: 장소별 게시글 목록을 반환
- Response (200):

```json
[
  {
    "place_id": "string",
    "posts": [
      { "post_id": 1, "post_title": "제목", "date": "2026-07-14T12:00:00Z" },
      { "post_id": 2, "post_title": "다른 제목", "date": "2026-07-13T09:00:00Z" }
    ]
  }
]
```

---

## 게시글 상세 조회
- Method: `GET`
- Endpoint: `/api/posts/{id}`
- Response (200):

```json
{
  "post_id": 1,
  "title": "게시글 제목",
  "contents": "본문 내용",
  "date": "2026-07-14T12:00:00Z"
}
```

---

## 게시글 작성
- Method: `POST`
- Endpoint: `/api/posts`
- Request JSON:

```json
{
  "post_title": "제목",
  "post_contents": "본문",
  "post_pwd": "비밀번호",
  "place_id": "place-123"
}
```
- Response (201):

```json
{ "post_success": true, "post_id": 123 }
```

---

## 게시글 수정
- Method: `PUT`
- Endpoint: `/api/posts/{id}`
- Request JSON:

```json
{
  "post_title": "수정된 제목",
  "post_contents": "수정된 본문",
  "post_pwd": "비밀번호"
}
```
- Responses:
  - 200 (성공): `{ "edit_success": true }`
  - 403 (비밀번호 불일치): `{ "success": false, "detail": "Wrong password" }`

---

## 게시글 삭제
- Method: `DELETE`
- Endpoint: `/api/posts/{id}`
- Request JSON:

```json
{ "post_pwd": "비밀번호" }
```
- Responses:
  - 200 (성공): `{ "delete_success": true }`
  - 403 (비밀번호 불일치): `{ "success": false, "detail": "Wrong password" }`

---

## 장소 조회
- Method: `GET`
- Endpoint: `/api/places`
- Query: `?category=축제` (선택)
- Response (200):

```json
[
  { "place_category": "관광지", "place_name": "경복궁", "lat": 37.5796, "lng": 126.9770 },
  { "place_category": "축제", "place_name": "서울빛축제", "lat": 37.56, "lng": 126.98 }
]
```

---

## 챗봇
- Method: `POST`
- Endpoint: `/api/chat`
- Request JSON:

```json
{ "chat_question": "명동 근처 맛집 알려줘" }
```
- Response (200):

```json
{ "chat_answer": "명동 근처 추천 맛집은 ..." }
```

---

파일 위치: `backend/docs/api_contract.md`

문제가 있으면 알려줘. 다음 단계로 FastAPI 프로젝트 초기 스캐폴딩을 진행할게.
