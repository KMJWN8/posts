from datetime import datetime
from typing import Optional

from ninja import Schema
from pydantic import ConfigDict


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

    model_config = ConfigDict(from_attributes=True)


class UserLoginRegisterSchema(Schema):
    user: UserOutSchema
    access: str
    refresh: str
