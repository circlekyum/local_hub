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

Run development server

```bash
uvicorn app.main:app --reload --port 8000
```

Health checks

- `GET /health`
- `GET /health/db`
# Backend (FastAPI)

Run locally:

```bash
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The API docs are available at `http://localhost:8000/docs` and a health endpoint at `/health`.
