from typing import List

from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.models.place import Place


def get_places(db: Session, category: str | None = None, keyword: str | None = None) -> List[Place]:
    stmt = select(Place)

    if category:
        # check multiple category fields
        stmt = stmt.where(or_(Place.cat1 == category, Place.cat2 == category, Place.cat3 == category))

    if keyword:
        stmt = stmt.where(Place.title.contains(keyword))

    return list(db.scalars(stmt).all())


def get_place(db: Session, place_id: str) -> Place | None:
    return db.get(Place, place_id)
