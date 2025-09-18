import pytest

pytestmark = pytest.mark.django_db


def test_register_success(create_user, client):
    resp = client.post(
        "/auth/register/", {"username": "newuser", "password": "StrongPass123"}
    )
    assert resp.status_code == 201
    assert "user" in resp.json()
    assert "access" in resp.json()


def test_register_fail(create_user, client):
    # Пустой username
    resp = client.post("/auth/register/", {"username": "", "password": "123"})
    assert resp.status_code == 400


def test_login_success(create_user, client):
    create_user(username="user1")
    resp = client.post("/auth/login/", {"username": "user1", "password": "pass123"})
    assert resp.status_code == 200
    assert "access" in resp.json()


def test_login_fail(create_user, client):
    create_user(username="user2")
    resp = client.post("/auth/login/", {"username": "user2", "password": "wrong"})
    assert resp.status_code == 401
