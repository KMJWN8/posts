from datetime import datetime
from typing import Optional

from ninja import Schema
from pydantic import ConfigDict

from src.users.schemas import UserOutSchema


class ArticleCreateSchema(Schema):
    title: str
    content: str


class ArticleUpdateSchema(Schema):
    title: Optional[str] = None
    content: Optional[str] = None


class ArticleOutSchema(Schema):
    id: int
    title: str
    content: str
    author: UserOutSchema
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
