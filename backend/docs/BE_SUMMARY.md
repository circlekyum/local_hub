# Backend Progress Summary

Short summary of work completed so far (BE-01 ~ BE-08).

**Scope completed**
- BE-01: FE/BE API contract agreed and saved to `backend/docs/api_contract.md`.
- BE-02: FastAPI scaffold created (`app/main.py`, `.env.example`, requirements).
- BE-03: Env / CORS / .gitignore configured; `backend/.env` template created.
- BE-04: SQLAlchemy + SQLite connection implemented (`app/database.py`, `data/community.db`).
- BE-05: `Post` SQLAlchemy model + Pydantic schemas added (`app/models/post.py`, `app/schemas/post.py`).
- BE-06: Posts API (list/detail/create) implemented and tested (`app/routers/posts.py`, `app/services/post_service.py`).
- BE-07: Password-checked update/delete implemented (service + router).
- BE-08: Global error handling and consistent error schemas added (`app/schemas/common.py`, `app/main.py` handlers), Swagger `responses` added.

**Key files changed/added**
- `app/main.py` — app entry, CORS, lifespan, exception handlers
- `app/database.py` — engine, SessionLocal, Base, create_tables, get_db
- `app/models/post.py` — `Post` SQLAlchemy model
- `app/schemas/post.py` — Pydantic request/response schemas
- `app/schemas/common.py` — `ErrorResponse`, `ValidationErrorResponse`
- `app/services/post_service.py` — DB operations + verify/update/delete
- `app/routers/posts.py` — REST endpoints for posts
- `backend/.env.example`, `backend/.env` — environment example and local template
- `backend/docs/api_contract.md`, `backend/docs/be_todo_schedule.md`, `backend/docs/be_03_env_cors.md`

**Notes & decisions**
- Passwords are stored in plaintext per RFP (education only). Do NOT use in production.
- API contract fields use `post_title`, `post_contents`, `post_pwd`, `place_id` for request bodies; responses use `id/title/contents/date` shapes per contract.
- Error responses are unified: validation → 422 with `detail`+`errors`; other errors use `detail`.
