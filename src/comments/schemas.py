from datetime import datetime
from typing import Optional

from ninja import Schema


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
    author: str
    created_at: datetime
    updated_at: datetime
