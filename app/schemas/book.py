from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.chapter import ChapterRead


class BookBase(BaseModel):
    title: str
    author_name: str
    series_name: Optional[str] = None
    series_order: Optional[int] = None
    description: Optional[str] = None


class BookCreate(BookBase):
    show_to_all: bool = True


class BookUpdate(BookBase):
    show_to_all: Optional[bool] = None


class BookRead(BookBase):
    id: int
    cover_path: str
    total_duration_seconds: int
    uploader_id: Optional[int] = None
    uploader_username: Optional[str] = None
    show_to_all: bool = True
    chapters: List[ChapterRead] = []

    model_config = ConfigDict(from_attributes=True)
