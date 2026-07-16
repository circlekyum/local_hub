Backend setup and quickstart
===========================

Prerequisites
- Python 3.11+ recommended

Create virtual environment and install dependencies

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# or bash
source .venv/Scripts/activate
pip install -r requirements.txt
```

Environment variables
- `DATABASE_PATH` (optional) — path to sqlite DB file (default `data/community.db`)
- `REGION_DB_PATH` (optional) — path to region attractions sqlite DB (default `data/region.db`)
- `OPENAI_API_KEY` (optional) — key for chat features
Environment variables
- Use `backend/.env` or set environment variables in your shell. A sample file is provided at `backend/.env.example`.
- `DATABASE_PATH` (optional) — path to sqlite DB file (default `data/community.db`)
- `REGION_DB_PATH` (optional) — path to region attractions sqlite DB (default `data/region.db`)
- `OPENAI_API_KEY` (optional) — key for chat features (store securely in CI/secret store for production)
- `ALLOWED_ORIGINS` — comma-separated origins allowed by CORS (default `http://localhost:5173`)

Notes on dependencies
- The OpenAI Python client requires a compatible `httpx` version. `requirements.txt` pins `openai==1.8.0` and `httpx==0.24.1` which are known to work together.

Run development server

```bash
export PYTHONPATH=backend
# load .env (optional)
set -o allexport; source backend/.env; set +o allexport
uvicorn app.main:app --reload --port 8000
```

Health checks

- `GET /health`
- `GET /health/db`
Additional tips
- If you change `.env`, restart the server (reloader may not pick up env changes for existing processes).
- For production, set secrets via your platform's secret manager (do not commit `.env` to source control).
# Backend (FastAPI)

Run locally:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API docs are available at `http://localhost:8000/docs` and a health endpoint at `/health`.
