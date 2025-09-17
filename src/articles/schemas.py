from datetime import datetime
from typing import Optional

from ninja import Schema


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
    author: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
