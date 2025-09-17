from django.db import models

from src.core.models import TimestampedModel
from src.users.models import User


class Article(TimestampedModel):
    title = models.CharField("title", max_length=200)
    content = models.TextField("content")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="author",
    )

    class Meta:
        db_table = "articles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
