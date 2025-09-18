from datetime import datetime
from typing import Optional

from ninja import Schema
from pydantic import ConfigDict

from src.users.schemas import UserOutSchema


class CommentCreateSchema(Schema):
    article_id: int
    content: str


class CommentUpdateSchema(Schema):
    content: Optional[str] = None


class CommentOutSchema(Schema):
    id: int
    content: str
    article_id: int
    article_title: str
    author: UserOutSchema
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def resolve_article_title(obj) -> str:
        return obj.article.title

    @staticmethod
    def resolve_article_id(obj) -> int:
        return obj.article.id

    model_config = ConfigDict(from_attributes=True)
