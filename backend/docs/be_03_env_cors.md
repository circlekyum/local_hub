# BE-03: 환경변수·CORS 설정 안내

요약: 백엔드에서 사용할 환경변수 파일 위치와 CORS 설정 방법을 정리합니다. OpenAI API 키 자리는 비워두었습니다 — 사용자가 직접 `backend/.env`에 값을 입력하세요.

파일
- 기본 예제: [backend/.env.example](backend/.env.example)

설정 방법
- 프로젝트 루트의 `backend` 폴더에 `.env` 파일을 생성하세요(예: `backend/.env`).
- 최소 항목(예시):

```env
OPENAI_API_KEY=
DATABASE_URL=sqlite:///./community.db
CORS_ORIGINS=http://localhost:5173
```

- **OpenAI API 키 자리:** `OPENAI_API_KEY=` 뒤에 키를 붙여 넣으세요. 현재 예제는 빈 값으로 남겨두었습니다.

CORS
- `CORS_ORIGINS`는 쉼표로 구분된 허용 출처 목록입니다. 예:

```env
CORS_ORIGINS=http://localhost:5173,https://your-frontend.netlify.app
```

`.gitignore`
- `.env` 및 `community.db`는 이미 `backend/.gitignore`에 포함되어 있어 커밋되지 않습니다. (확인 경로: [backend/.gitignore](backend/.gitignore))

검증
- 서버가 실행 중일 때 `GET /health`로 기본 응답을 확인하세요:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

보안 주의
- `.env` 파일은 비밀을 포함하므로 절대 원격 저장소에 올리지 마세요.
