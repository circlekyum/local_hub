from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    contents = Column(Text, nullable=False)
    pwd = Column(String(128), nullable=False)
    place_id = Column(String(100), nullable=True, index=True)
    date_created = Column(DateTime, default=datetime.utcnow)
