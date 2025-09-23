from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


class AuthAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
        )

        self.login_url = "/api/v1/auth/login/"
        self.register_url = "/api/v1/auth/register/"
        self.refresh_url = "/api/v1/auth/refresh/"
        self.logout_url = "/api/v1/auth/logout/"

    def test_login_success(self):
        """Успешный логин"""
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access", data)
        self.assertIn("refresh", data)

    def test_login_invalid_credentials(self):
        """Логин с неверными данными"""
        response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "wrongpass"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid credentials"})

    def test_register_success(self):
        """Успешная регистрация"""
        response = self.client.post(
            self.register_url,
            {"username": "newuser", "password": "newpass123"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "User registered successfully")
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_duplicate_username(self):
        """Регистрация с уже существующим username"""
        response = self.client.post(
            self.register_url,
            {"username": "testuser", "password": "newpass123"},  # уже существует
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Username already exists"})

    def test_refresh_token_success(self):
        """Успешное обновление токена"""
        # Сначала логинимся, чтобы получить refresh токен
        login_response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        refresh_token = login_response.json()["refresh"]

        response = self.client.post(
            self.refresh_url, {"refresh": refresh_token}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_refresh_token_invalid(self):
        """Обновление с неверным refresh токеном"""
        response = self.client.post(
            self.refresh_url, {"refresh": "invalid.token.here"}, format="json"
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": "Invalid refresh token"})

    def test_logout_authenticated_user(self):
        """Успешный logout аутентифицированного пользователя"""
        # Сначала логинимся
        login_response = self.client.post(
            self.login_url,
            {"username": "testuser", "password": "testpass123"},
            format="json",
        )
        access_token = login_response.json()["access"]

        # Выполняем logout
        response = self.client.post(
            self.logout_url, HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"success": True})

    def test_logout_unauthenticated_user(self):
        """Logout без аутентификации"""
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 401)

    def test_register_creates_user_in_database(self):
        """Проверка, что регистрация действительно создает пользователя"""
        initial_count = User.objects.count()

        self.client.post(
            self.register_url,
            {"username": "database_test_user", "password": "testpass123"},
            format="json",
        )

        self.assertEqual(User.objects.count(), initial_count + 1)
        self.assertTrue(User.objects.filter(username="database_test_user").exists())
