from typing import List

from ninja import Router

from src.core.auth import jwt_auth
from src.core.services import check_ownership

from .schemas import ArticleCreateSchema, ArticleOutSchema, ArticleUpdateSchema
from .services import ArticleCRUD

router = Router(tags=["Articles"])


@router.get("/", response=List[ArticleOutSchema])
def list_articles(request):
    objs = ArticleCRUD.list()
    return [ArticleOutSchema.from_orm(a) for a in objs]


@router.get("/{article_id}", response=ArticleOutSchema)
def get_article(request, article_id: int):
    obj = ArticleCRUD.retrieve(article_id)
    return ArticleOutSchema.from_orm(obj)


@router.post("/", response=ArticleOutSchema, auth=jwt_auth)
def create_article(request, payload: ArticleCreateSchema):
    data = payload.dict()
    data["author_id"] = request.user.id
    obj = ArticleCRUD.create(data)
    return ArticleOutSchema.from_orm(obj)


@router.put("/{article_id}", response=ArticleOutSchema, auth=jwt_auth)
def update_article(request, article_id: int, payload: ArticleUpdateSchema):
    article = ArticleCRUD.get_object(article_id)
    check_ownership(article.author, request.user)
    data = payload.dict(exclude_unset=True)
    obj = ArticleCRUD.update(article_id, data, user=request.user)
    return ArticleOutSchema.from_orm(obj)


@router.delete("/{article_id}", auth=jwt_auth)
def delete_article(request, article_id: int):
    article = ArticleCRUD.get_object(article_id)
    check_ownership(article.author, request.user)
    ArticleCRUD.delete(article_id, user=request.user)
    return {"success": True}
