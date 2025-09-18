import pytest
from django.contrib.auth.models import User
from django.test import Client

pytestmark = pytest.mark.django_db


# -----------------------------
# Пользователь
# -----------------------------
@pytest.fixture
def create_user():
    """Функция для создания пользователя"""

    def _create_user(username="user", password="pass123"):
        return User.objects.create_user(username=username, password=password)

    return _create_user


# -----------------------------
# Клиент с JWT
# -----------------------------
@pytest.fixture
def auth_client(create_user):
    """Возвращает клиент с JWT токеном"""
    client = Client()
    user = create_user()
    # Получаем токен через /auth/login/
    resp = client.post(
        "/auth/login/", {"username": user.username, "password": "pass123"}
    )
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    return client, user


# -----------------------------
# Создание статьи через API
# -----------------------------
@pytest.fixture
def create_article(auth_client):
    client, user = auth_client

    def _create_article(title="Title", content="Content"):
        resp = client.post(
            "/articles/",
            {"title": title, "content": content},
            content_type="application/json",
        )
        return resp.json()

    return _create_article, client, user


# -----------------------------
# Создание комментария через API
# -----------------------------
@pytest.fixture
def create_comment(create_article, auth_client):
    create_article_fn, client, user = create_article
    article = create_article_fn()

    def _create_comment(content="Comment"):
        resp = client.post(
            "/comments/",
            {"article_id": article["id"], "content": content},
            content_type="application/json",
        )
        return resp.json()

    return _create_comment, client, user, article
