from sqlalchemy import Float, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Place(Base):
    __tablename__ = "attractions"

    # DB uses contentid as primary key (string)
    contentid: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=True, index=True)
    addr1: Mapped[str | None] = mapped_column(String, nullable=True)
    addr2: Mapped[str | None] = mapped_column(String, nullable=True)
    zipcode: Mapped[str | None] = mapped_column(String, nullable=True)
    tel: Mapped[str | None] = mapped_column(String, nullable=True)
    firstimage: Mapped[str | None] = mapped_column(String, nullable=True)
    firstimage2: Mapped[str | None] = mapped_column(String, nullable=True)
    cpyrhtDivCd: Mapped[str | None] = mapped_column(String, nullable=True)
    mapx: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    mapy: Mapped[float | None] = mapped_column(Float, nullable=True, index=True)
    mlevel: Mapped[int | None] = mapped_column(Integer, nullable=True)
    createdtime = mapped_column(DateTime, nullable=True)
    modifiedtime = mapped_column(DateTime, nullable=True)
    contenttypeid: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    areacode: Mapped[str | None] = mapped_column(String, nullable=True)
    cat1: Mapped[str | None] = mapped_column(String, nullable=True)
    cat2: Mapped[str | None] = mapped_column(String, nullable=True)
    cat3: Mapped[str | None] = mapped_column(String, nullable=True)
    sigungucode: Mapped[str | None] = mapped_column(String, nullable=True)
    lDongRegnCd: Mapped[str | None] = mapped_column(String, nullable=True)
    lDongSignguCd: Mapped[str | None] = mapped_column(String, nullable=True)
    lclsSystm1: Mapped[str | None] = mapped_column(String, nullable=True)
    lclsSystm2: Mapped[str | None] = mapped_column(String, nullable=True)
    lclsSystm3: Mapped[str | None] = mapped_column(String, nullable=True)
    raw: Mapped[str | None] = mapped_column(Text, nullable=True)
