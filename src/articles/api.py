from typing import List

from django.core.exceptions import PermissionDenied
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from .schemas import ArticleCreateSchema, ArticleOutSchema, ArticleUpdateSchema
from .services import ArticleCRUD

router = Router(auth=JWTAuth(), tags=["Articles"])


@router.get("/", response=List[ArticleOutSchema])
def list_articles(request):
    return ArticleCRUD.list()


@router.get("/{article_id}", response=ArticleOutSchema)
def get_article(request, article_id: int):
    return ArticleCRUD.retrieve(article_id)


@router.post("/", response=ArticleOutSchema)
def create_article(request, payload: ArticleCreateSchema):
    data = payload.dict()
    data["author"] = request.user
    return ArticleCRUD.create(data)


@router.put("/{article_id}", response=ArticleOutSchema)
def update_article(request, article_id: int, payload: ArticleUpdateSchema):
    article = ArticleCRUD.get_object(article_id)
    if article.author != request.user:
        raise PermissionDenied("You can only edit your own articles")
    data = payload.dict(exclude_unset=True)
    return ArticleCRUD.update(article_id, data)


@router.delete("/{article_id}")
def delete_article(request, article_id: int):
    article = ArticleCRUD.get_object(article_id)
    if article.author != request.user:
        raise PermissionDenied("You can only delete your own articles")
    ArticleCRUD.delete(article_id)
    return {"success": True}
