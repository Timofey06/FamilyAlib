from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer


class ProgressCreate(BaseModel):
    book_id: int
    current_chapter_id: Optional[int] = None
    current_position_seconds: int
    completion_percent: int = 0
    is_finished: bool = False


class ProgressRead(BaseModel):
    book_id: int
    current_chapter_id: Optional[int] = None
    current_position_seconds: int
    completion_percent: int
    is_favorite: bool
    is_finished: bool
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('updated_at')
    def serialize_updated_at(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat()
