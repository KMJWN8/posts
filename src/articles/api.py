from typing import List

from django.core.exceptions import PermissionDenied
from ninja import Router
from ninja_jwt.authentication import JWTAuth

from .schemas import ArticleCreateSchema, ArticleOutSchema, ArticleUpdateSchema
from .services import ArticleCRUD

router = Router(auth=JWTAuth(), tags=["Articles"])


@router.get("/", response=List[ArticleOutSchema])
def list_articles(request):
    objs = ArticleCRUD.list()
    return [ArticleOutSchema.from_orm(a) for a in objs]


@router.get("/{article_id}", response=ArticleOutSchema)
def get_article(request, article_id: int):
    obj = ArticleCRUD.retrieve(article_id)
    return ArticleOutSchema.from_orm(obj)


@router.post("/", response=ArticleOutSchema)
def create_article(request, payload: ArticleCreateSchema):
    data = payload.dict()
    data["author_id"] = request.user.id
    obj = ArticleCRUD.create(data)
    return ArticleOutSchema.from_orm(obj)


@router.put("/{article_id}", response=ArticleOutSchema)
def update_article(request, article_id: int, payload: ArticleUpdateSchema):
    article = ArticleCRUD.get_object(article_id)
    if article.author != request.user:
        raise PermissionDenied("You can only edit your own articles")
    data = payload.dict(exclude_unset=True)
    obj = ArticleCRUD.update(article_id, data, user=request.user)


@router.delete("/{article_id}")
def delete_article(request, article_id: int):
    article = ArticleCRUD.get_object(article_id)
    if article.author != request.user:
        raise PermissionDenied("You can only delete your own articles")
    ArticleCRUD.delete(article_id, user=request.user)
    return {"success": True}
