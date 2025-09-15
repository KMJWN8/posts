from django.db import models

from src.users.models import User


class Article(models.Model):
    title = models.CharField("title", max_length=200)
    content = models.TextField("content")

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="articles",
        verbose_name="author",
    )

    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        db_table = "articles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
