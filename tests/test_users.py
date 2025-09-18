import pytest

pytestmark = pytest.mark.django_db


def test_list_users(auth_client):
    client, _ = auth_client
    resp = client.get("/users/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_user(auth_client):
    client, user = auth_client
    resp = client.get(f"/users/{user.id}/")
    assert resp.status_code == 200
    assert resp.json()["id"] == user.id


def test_update_user_success(auth_client):
    client, user = auth_client
    resp = client.put(
        f"/users/{user.id}/", {"bio": "Updated"}, content_type="application/json"
    )
    assert resp.status_code == 200
    assert resp.json()["bio"] == "Updated"


def test_update_user_forbidden(auth_client, create_user):
    client, _ = auth_client
    other = create_user(username="other")
    # Создаём JWT для другого пользователя
    resp = client.post("/auth/login/", {"username": "other", "password": "pass123"})
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    # Пытаемся обновить чужой профиль
    resp = client.put(f"/users/1/", {"bio": "Hack"}, content_type="application/json")
    assert resp.status_code == 403


def test_delete_user_success(auth_client):
    client, user = auth_client
    resp = client.delete(f"/users/{user.id}/")
    assert resp.status_code == 200


def test_delete_user_forbidden(auth_client, create_user):
    client, user = auth_client
    other = create_user(username="other")
    resp = client.post("/auth/login/", {"username": "other", "password": "pass123"})
    access = resp.json()["access"]
    client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {access}"
    resp = client.delete(f"/users/{user.id}/")
    assert resp.status_code == 403
