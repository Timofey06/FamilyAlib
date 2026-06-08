from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.models import Base


class UserBookProgress(Base):
    __tablename__ = 'user_book_progress'

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id', ondelete='CASCADE'), primary_key=True)
    current_chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=True)
    current_position_seconds = Column(Integer, default=0, nullable=False)
    completion_percent = Column(Integer, default=0, nullable=False)
    is_favorite = Column(Boolean, default=False, nullable=False)
    is_finished = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    book = relationship('Book', back_populates='progress')
