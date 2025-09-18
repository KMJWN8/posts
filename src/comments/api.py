from typing import List

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ninja import Router

from src.articles.models import Article
from src.core.auth import jwt_auth
from src.core.services import check_ownership

from .schemas import CommentCreateSchema, CommentOutSchema, CommentUpdateSchema
from .services import CommentCRUD

router = Router(tags=["Comments"])


@router.get("/", response=List[CommentOutSchema])
def list_comments(request):
    return CommentCRUD.list()


@router.get("/{comment_id}", response=CommentOutSchema)
def get_comment(request, comment_id: int):
    return CommentCRUD.retrieve(comment_id)


@router.post("/", response=CommentOutSchema, auth=jwt_auth)
def create_comment(request, payload: CommentCreateSchema):
    data = payload.dict()
    data["article"] = get_object_or_404(Article, id=data.pop("article_id"))
    data["author_id"] = request.user.id
    return CommentCRUD.create(data)


@router.put("/{comment_id}", response=CommentOutSchema, auth=jwt_auth)
def update_comment(request, comment_id: int, payload: CommentUpdateSchema):
    comment = CommentCRUD.get_object(comment_id)
    check_ownership(comment.author, request.user)
    data = payload.dict(exclude_unset=True)
    return CommentCRUD.update(comment_id, data)


@router.delete("/{comment_id}", auth=jwt_auth)
def delete_comment(request, comment_id: int):
    comment = CommentCRUD.get_object(comment_id)
    check_ownership(comment.author, request.user)
    CommentCRUD.delete(comment_id)
    return {"success": True}
