from fastapi import APIRouter, Query
from typing import List, Optional
import json
from pathlib import Path

from app.schemas.place import PlaceResponse
from app.config import settings

router = APIRouter(prefix="/api", tags=["places"])


@router.get("/places", response_model=List[PlaceResponse], summary="지역 장소 목록 조회")
def list_places(category: Optional[str] = Query(None)):
    results = []
    # Prefer configured region data file if present
    data_file = settings.region_data_file
    files = [data_file] if data_file.exists() else list(Path(__file__).resolve().parents[2].glob("*.json"))
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            # Expect list of places or dict; attempt to extract
            if isinstance(data, list):
                for item in data:
                    if category and item.get("category") != category:
                        continue
                    results.append({
                        "name": item.get("name") or item.get("place_name") or "",
                        "category": item.get("category") or p.stem,
                        "region": item.get("region") or "",
                        "address": item.get("address"),
                        "latitude": item.get("lat"),
                        "longitude": item.get("lng"),
                        "description": item.get("description"),
                    })
        except Exception:
            continue
    return results
