from datetime import datetime
from typing import Optional

from ninja import Schema


class UserCreateSchema(Schema):
    username: str
    password: str


class UserUpdateSchema(Schema):
    username: Optional[str] = None
    password: Optional[str] = None
    bio: Optional[str] = None


class UserOutSchema(Schema):
    id: int
    username: str
    bio: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserLoginRegisterSchema(Schema):
    user: UserOutSchema
    access: str
    refresh: str
