from src.articles.models import Article
from src.core.services import BaseCRUD

from .schemas import ArticleCreateSchema, ArticleOutSchema, ArticleUpdateSchema


class ArticleCRUD(BaseCRUD):
    model = Article
    create_schema = ArticleCreateSchema
    update_schema = ArticleUpdateSchema
    out_schema = ArticleOutSchema

    @classmethod
    def get_queryset(cls):
        # подгружаем автора чтобы избежать N+1 запрос
        return cls.model.objects.select_related("author").all()
