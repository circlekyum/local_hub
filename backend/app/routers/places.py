from fastapi import APIRouter, Query
from typing import List, Optional
import json
from pathlib import Path

router = APIRouter(prefix="/api/places", tags=["places"])


@router.get("")
def list_places(category: Optional[str] = Query(None)):
    # Attempt to load JSON files from workspace root `c:\\Users\\SSAFY\\Desktop\\vibe_team`
    base = Path(__file__).resolve().parents[2]
    results = []
    for p in base.glob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # Expect list of places or dict; attempt to extract
            if isinstance(data, list):
                for item in data:
                    if category and item.get("category") != category:
                        continue
                    results.append({
                        "place_category": item.get("category") or p.stem,
                        "place_name": item.get("name") or item.get("place_name") or "",
                        "lat": item.get("lat"),
                        "lng": item.get("lng"),
                    })
        except Exception:
            continue
    return results
