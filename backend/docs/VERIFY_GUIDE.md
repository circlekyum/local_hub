# Verify Backend Locally (quick)

Prereqs
- Python 3.10+
- venv (recommended) at C:\Users\SSAFY\Desktop\venv

Setup (inside terminal)
1. Activate venv (PowerShell):
   C:\Users\SSAFY\Desktop\venv\Scripts\Activate.ps1
2. Install deps:
   python -m pip install --upgrade pip
   python -m pip install -r backend/requirements.txt
3. Create .env from example:
   copy backend\.env.example backend\.env
   (fill OPENAI_API_KEY if needed)

Run server (from backend folder):
   /c/Users/SSAFY/Desktop/venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

Health checks:
   curl http://127.0.0.1:8000/health
   curl http://127.0.0.1:8000/health/db

Quick API examples (use files to avoid quoting issues):
  echo '{"post_title":"verify","post_contents":"내용","post_pwd":"pw","place_id":"area"}' > post.json
  curl -i -X POST http://127.0.0.1:8000/api/posts -H "Content-Type: application/json" --data @post.json

  curl -s http://127.0.0.1:8000/api/posts
  curl -s http://127.0.0.1:8000/api/posts/1

Update (wrong pwd)
  echo '{"post_title":"x","post_contents":"y","post_pwd":"wrong"}' > put.json
  curl -i -X PUT http://127.0.0.1:8000/api/posts/1 -H "Content-Type: application/json" --data @put.json

Delete
  echo '{"post_pwd":"pw"}' > del.json
  curl -i -X DELETE http://127.0.0.1:8000/api/posts/1 -H "Content-Type: application/json" --data @del.json

DB checks:
  ls backend\data\community.db
  /c/Users/SSAFY/Desktop/venv/Scripts/python.exe -c "from sqlalchemy import inspect; from app.database import engine; print(inspect(engine).get_table_names())"

If the server fails to import:
  /c/Users/SSAFY/Desktop/venv/Scripts/python.exe -c "from app.main import app; print('FastAPI import success')"

Notes
- Error format: validation -> 422 with 'detail' and 'errors' array; others -> 'detail'.
- Swagger UI: http://127.0.0.1:8000/docs
