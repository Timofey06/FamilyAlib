from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class PasswordUpdate(BaseModel):
    password: str


class UserRead(UserBase):
    id: int
    is_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
