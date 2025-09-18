# apps/comments/api.py

from typing import List

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ninja import Router

from src.articles.models import Article
from src.core.auth import jwt_auth

from .schemas import CommentCreateSchema, CommentOutSchema, CommentUpdateSchema
from .services import CommentCRUD

router = Router(tags=["Comments"])


@router.get("/", response=List[CommentOutSchema])
def list_comments(request):
    qs = CommentCRUD.list()
    return [CommentOutSchema.from_orm(c) for c in qs]


@router.get("/{comment_id}", response=CommentOutSchema)
def get_comment(request, comment_id: int):
    q = CommentCRUD.retrieve(comment_id)
    return CommentOutSchema.from_orm(q)


@router.post("/", response=CommentOutSchema, auth=jwt_auth)
def create_comment(request, payload: CommentCreateSchema):
    data = payload.dict()
    data["article"] = get_object_or_404(Article, id=data.pop("article_id"))
    data["author_id"] = request.user.id
    obj = CommentCRUD.create(data)
    return CommentOutSchema.from_orm(obj)


@router.put("/{comment_id}", response=CommentOutSchema, auth=jwt_auth)
def update_comment(request, comment_id: int, payload: CommentUpdateSchema):
    comment = CommentCRUD.get_object(comment_id)
    if comment.author != request.user:
        raise PermissionDenied("You can only edit your own comments")
    data = payload.dict(exclude_unset=True)
    obj = CommentCRUD.update(comment_id, data)
    return CommentOutSchema.from_orm(obj)


@router.delete("/{comment_id}", auth=jwt_auth)
def delete_comment(request, comment_id: int):
    comment = CommentCRUD.get_object(comment_id)
    if comment.author != request.user:
        raise PermissionDenied("You can only delete your own comments")
    CommentCRUD.delete(comment_id)
    return {"success": True}
