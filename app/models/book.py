from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.models import Base


class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author_name = Column(String(255), nullable=False)
    series_name = Column(String(255), nullable=True)
    series_order = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    cover_path = Column(String(255), nullable=False)
    uploader_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    show_to_all = Column(Boolean, default=True, nullable=False)
    total_duration_seconds = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    chapters = relationship('Chapter', back_populates='book', cascade='all, delete-orphan')
    progress = relationship('UserBookProgress', back_populates='book', cascade='all, delete-orphan')
    uploader = relationship('User')

    @property
    def uploader_username(self):
        return self.uploader.username if self.uploader else None
