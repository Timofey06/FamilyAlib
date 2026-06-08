from pydantic import BaseModel, ConfigDict


class ChapterRead(BaseModel):
    id: int
    title: str
    chapter_number: int
    duration_seconds: int
    file_path: str

    model_config = ConfigDict(from_attributes=True)
