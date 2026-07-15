from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.place import PlaceResponse
from app.services import place_service

router = APIRouter(prefix="/api/places", tags=["places"])


DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[PlaceResponse], summary="지역 장소 목록 조회")
def read_places(db: DbSession, category: str | None = Query(None), keyword: str | None = Query(None)):
    places = place_service.get_places(db=db, category=category, keyword=keyword)

    results = []
    for p in places:
        results.append(
            PlaceResponse(
                id=p.contentid,
                name=p.title,
                category=(p.cat1 or p.cat2 or p.cat3),
                address=p.addr1,
                latitude=p.mapy,
                longitude=p.mapx,
                description=(p.raw[:500] if p.raw else None),
                tel=p.tel,
            )
        )

    return results


@router.get("/{place_id}", response_model=PlaceResponse)
def read_place(place_id: str, db: DbSession):
    place = place_service.get_place(db, place_id)
    if place is None:
        raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")

    return PlaceResponse(
        id=place.contentid,
        name=place.title,
        category=(place.cat1 or place.cat2 or place.cat3),
        address=place.addr1,
        latitude=place.mapy,
        longitude=place.mapx,
        description=(place.raw[:500] if place.raw else None),
        tel=place.tel,
    )
