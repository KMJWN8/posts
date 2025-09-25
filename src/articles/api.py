from typing import List

from ninja import Router
from ninja_extra import permissions

from src.core.auth import jwt_auth
from src.core.services import check_ownership

from .schemas import ArticleCreateSchema, ArticleOutSchema, ArticleUpdateSchema
from .services import ArticleCRUD

router = Router(tags=["Articles"])


@router.get(
    "/", response=List[ArticleOutSchema], permissions=[permissions.IsAuthenticated]
)
def list_articles(request):
    return ArticleCRUD.list()


@router.get(
    "/{article_id}",
    response=ArticleOutSchema,
    permissions=[permissions.IsAuthenticatedOrReadOnly],
)
def get_article(request, article_id: int):
    return ArticleCRUD.retrieve(article_id)


@router.post(
    "/",
    response=ArticleOutSchema,
    permissions=[permissions.IsAuthenticated],
    auth=jwt_auth,
)
def create_article(request, payload: ArticleCreateSchema):
    return ArticleCRUD.create({**payload.dict(), "author_id": request.user.id})


@router.put(
    "/{article_id}",
    response=ArticleOutSchema,
    permissions=[permissions.IsAuthenticated],
    auth=jwt_auth,
)
def update_article(request, article_id: int, payload: ArticleUpdateSchema):
    article = ArticleCRUD.get_object(article_id)
    check_ownership(article.author, request.user)
    data = payload.dict(exclude_unset=True)
    return ArticleCRUD.update(article_id, data, user_id=request.user.id)


@router.delete(
    "/{article_id}", permissions=[permissions.IsAuthenticated], auth=jwt_auth
)
def delete_article(request, article_id: int):
    article = ArticleCRUD.get_object(article_id)
    check_ownership(article.author, request.user)
    ArticleCRUD.delete(article_id, user_id=request.user.id)
    return {"success": True}
