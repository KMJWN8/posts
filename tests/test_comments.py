import pytest

pytestmark = pytest.mark.django_db


def test_create_comment_success(create_comment):
    create_comment_fn, client, _, _ = create_comment
    resp = create_comment_fn("Nice comment")
    assert resp["content"] == "Nice comment"


def test_create_comment_fail_empty(create_comment):
    create_comment_fn, client, _, _ = create_comment
    resp = client.post(
        "/comments/", {"article_id": 1, "content": ""}, content_type="application/json"
    )
    assert resp.status_code == 400


def test_update_comment_success(create_comment):
    create_comment_fn, client, _, _ = create_comment
    comment = create_comment_fn("Edit me")
    resp = client.put(
        f'/comments/{comment["id"]}/',
        {"content": "Edited"},
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.json()["content"] == "Edited"


def test_update_comment_forbidden(create_comment, create_user):
    create_comment_fn, client, _, _ = create_comment
    comment = create_comment_fn("Test")
    other = create_user(username="other")
    resp = client.post("/auth/login/", {"username": "other", "password": "pass123"})
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    resp = client.put(
        f'/comments/{comment["id"]}/',
        {"content": "Hack"},
        content_type="application/json",
    )
    assert resp.status_code == 403


def test_delete_comment_success(create_comment):
    create_comment_fn, client, _, _ = create_comment
    comment = create_comment_fn("Delete me")
    resp = client.delete(f'/comments/{comment["id"]}/')
    assert resp.status_code == 200


def test_delete_comment_forbidden(create_comment, create_user):
    create_comment_fn, client, _, _ = create_comment
    comment = create_comment_fn("Test")
    other = create_user(username="other")
    resp = client.post("/auth/login/", {"username": "other", "password": "pass123"})
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    resp = client.delete(f'/comments/{comment["id"]}/')
    assert resp.status_code == 403
