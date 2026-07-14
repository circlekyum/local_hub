import os, sys, json
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from postgrest.exceptions import APIError

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
if not SUPABASE_URL or not SUPABASE_KEY:
    print("Set SUPABASE_URL and SUPABASE_KEY environment variables")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE = Path(__file__).resolve().parent
json_path = BASE / "seoul_data" / "seoul_attraction.json"
if not json_path.exists():
    print("JSON 파일을 찾을 수 없습니다:", json_path)
    sys.exit(1)

def find_items(obj):
    if isinstance(obj, list):
        if all(isinstance(x, dict) for x in obj):
            return obj
        for e in obj:
            r = find_items(e)
            if r: return r
    elif isinstance(obj, dict):
        for v in obj.values():
            r = find_items(v)
            if r: return r
    return None

with json_path.open("r", encoding="utf-8") as f:
    raw = json.load(f)

items = find_items(raw)
if not items:
    print("배열(items) 구조를 찾을 수 없습니다. JSON 구조를 확인하세요.")
    sys.exit(1)

FIELDS = ["contentid","contenttypeid","title","addr1","addr2","zipcode","tel","mapx","mapy",
          "mlevel","areacode","sigungucode","lDongRegnCd","lDongSignguCd",
          "firstimage","firstimage2","lclsSystm1","lclsSystm2","lclsSystm3"]

def normalize(it):
    out = {}
    for k in FIELDS:
        db_k = k.lower()               # DB에 저장된 컬럼명(소문자)
        v = it.get(k)
        if v in ("", None):
            out[db_k] = None
            continue
        if k in ("contentid","contenttypeid","mlevel","areacode","sigungucode"):
            try: out[db_k] = int(v)
            except: out[db_k] = None
        elif k in ("mapx","mapy"):
            try: out[db_k] = float(v)
            except: out[db_k] = None
        else:
            out[db_k] = v
    return out

rows = [normalize(it) for it in items]
rows = [r for r in rows if r.get("contentid")]

# 테이블 존재 확인
try:
    supabase.table("seoul_attractions").select("contentid").limit(1).execute()
except APIError as e:
    print("테이블 'seoul_attractions'를 찾을 수 없습니다. 먼저 Supabase에서 CREATE TABLE 실행하세요.")
    print(e)
    sys.exit(1)

BATCH = 500
for i in range(0, len(rows), BATCH):
    batch = rows[i:i+BATCH]
    resp = supabase.table("seoul_attractions").insert(batch).execute()
    print("Inserted rows", i, "->", getattr(resp, "status_code", None))

print("완료. 총 업로드 레코드:", len(rows))