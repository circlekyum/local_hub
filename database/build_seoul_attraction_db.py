# load_attractions.py
import json
from datetime import datetime
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, DateTime, Text, Index
)
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class Attraction(Base):
    __tablename__ = "attractions"
    contentid = Column(String, primary_key=True, index=True)
    title = Column(String, index=True)
    addr1 = Column(String)
    addr2 = Column(String)
    zipcode = Column(String)
    tel = Column(String)
    firstimage = Column(String)
    firstimage2 = Column(String)
    cpyrhtDivCd = Column(String)
    mapx = Column(Float, index=True)
    mapy = Column(Float, index=True)
    mlevel = Column(Integer)
    createdtime = Column(DateTime, index=True)
    modifiedtime = Column(DateTime)
    contenttypeid = Column(Integer, index=True)
    areacode = Column(String)
    cat1 = Column(String)
    cat2 = Column(String)
    cat3 = Column(String)
    sigungucode = Column(String)
    lDongRegnCd = Column(String)
    lDongSignguCd = Column(String)
    lclsSystm1 = Column(String)
    lclsSystm2 = Column(String)
    lclsSystm3 = Column(String)
    raw = Column(Text)

Index("ix_attractions_map", Attraction.mapx, Attraction.mapy)

def parse_dt(s: str):
    if not s:
        return None
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def load_json_to_db(json_path: str, db_url: str = "sqlite:///seoul_attractions.db"):
    engine = create_engine(db_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine, future=True)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items") or []

    with Session() as session:
        for it in items:
            try:
                mapx = float(it["mapx"]) if it.get("mapx") else None
            except Exception:
                mapx = None
            try:
                mapy = float(it["mapy"]) if it.get("mapy") else None
            except Exception:
                mapy = None
            try:
                mlevel = int(it["mlevel"]) if it.get("mlevel") and str(it["mlevel"]).isdigit() else None
            except Exception:
                mlevel = None
            try:
                contenttypeid = int(it["contenttypeid"]) if it.get("contenttypeid") and str(it["contenttypeid"]).isdigit() else None
            except Exception:
                contenttypeid = None

            obj = Attraction(
                contentid=it.get("contentid"),
                title=it.get("title"),
                addr1=it.get("addr1"),
                addr2=it.get("addr2"),
                zipcode=it.get("zipcode"),
                tel=it.get("tel"),
                firstimage=it.get("firstimage"),
                firstimage2=it.get("firstimage2"),
                cpyrhtDivCd=it.get("cpyrhtDivCd"),
                mapx=mapx,
                mapy=mapy,
                mlevel=mlevel,
                createdtime=parse_dt(it.get("createdtime", "")),
                modifiedtime=parse_dt(it.get("modifiedtime", "")),
                contenttypeid=contenttypeid,
                areacode=it.get("areacode"),
                cat1=it.get("cat1"),
                cat2=it.get("cat2"),
                cat3=it.get("cat3"),
                sigungucode=it.get("sigungucode"),
                lDongRegnCd=it.get("lDongRegnCd"),
                lDongSignguCd=it.get("lDongSignguCd"),
                lclsSystm1=it.get("lclsSystm1"),
                lclsSystm2=it.get("lclsSystm2"),
                lclsSystm3=it.get("lclsSystm3"),
                raw=json.dumps(it, ensure_ascii=False)
            )
            session.merge(obj)
        session.commit()

if __name__ == "__main__":
    load_json_to_db("seoul_data/seoul_attraction.json")