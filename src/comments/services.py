from src.comments.models import Comment
from src.core.services import BaseCRUD

from .schemas import CommentCreateSchema, CommentOutSchema, CommentUpdateSchema


class CommentCRUD(BaseCRUD):
    model = Comment
    create_schema = CommentCreateSchema
    update_schema = CommentUpdateSchema
    out_schema = CommentOutSchema
