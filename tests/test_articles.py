import pytest

pytestmark = pytest.mark.django_db


def test_create_article_success(create_article):
    create_article_fn, client, _ = create_article
    resp = client.post(
        "/articles/",
        {"title": "Test", "content": "Content"},
        content_type="application/json",
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test"


def test_create_article_fail_no_auth(create_article):
    create_article_fn, client, _ = create_article
    client.defaults.pop("HTTP_AUTHORIZATION", None)  # убираем JWT
    resp = client.post(
        "/articles/",
        {"title": "Fail", "content": "Content"},
        content_type="application/json",
    )
    assert resp.status_code == 401


def test_update_article_success(create_article):
    create_article_fn, client, _ = create_article
    article = create_article_fn()
    resp = client.put(
        f'/articles/{article["id"]}/',
        {"title": "Updated"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated"


def test_update_article_forbidden(create_article, create_user):
    create_article_fn, client, user = create_article
    article = create_article_fn()
    other = create_user(username="other")
    resp = client.post("/auth/login/", {"username": "other", "password": "pass123"})
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    resp = client.put(
        f'/articles/{article["id"]}/',
        {"title": "Hack"},
        content_type="application/json",
    )
    assert resp.status_code == 403


def test_delete_article_success(create_article):
    create_article_fn, client, _ = create_article
    article = create_article_fn()
    resp = client.delete(f'/articles/{article["id"]}/')
    assert resp.status_code == 200


def test_delete_article_forbidden(create_article, create_user):
    create_article_fn, client, user = create_article
    article = create_article_fn()
    other = create_user(username="other")
    resp = client.post("/auth/login/", {"username": "other", "password": "pass123"})
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    resp = client.delete(f'/articles/{article["id"]}/')
    assert resp.status_code == 403
