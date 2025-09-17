from django.contrib.auth.models import AbstractUser
from django.db import models

from src.core.models import TimestampedModel


class User(AbstractUser, TimestampedModel):
    bio = models.TextField("bio", blank=True, default="", max_length=500)
    avatar = models.ImageField("avatar", upload_to="avatars/", blank=True, null=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username
