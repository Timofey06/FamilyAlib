from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models import Base


class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    file_path = Column(String(255), nullable=False)

    book = relationship('Book', back_populates='chapters')
