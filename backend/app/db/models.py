from sqlalchemy import Column, Integer, String, Text
from app.db.database import Base

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    summary = Column(Text)