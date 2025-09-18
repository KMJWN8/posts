# tests/test_users.py
from django.test import TestCase
from rest_framework.test import APIClient

from src.users.models import User


class UsersAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="user1",
            email="u1@example.com",
            password="pass1234",
            first_name="John",
            bio="Old bio",
        )
        self.other_user = User.objects.create_user(
            username="user2", email="u2@example.com", password="pass1234"
        )

        self.list_url = "/api/v1/users/"
        self.detail_url = f"/api/v1/users/{self.user.id}/"
        self.update_url = f"/api/v1/users/{self.user.id}/"
        self.delete_url = f"/api/v1/users/{self.user.id}/"

    def test_list_users_authenticated_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_list_users_unauthenticated_forbidden(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 403)

    def test_retrieve_user_success(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "user1")

    def test_update_user_own_profile_success(self):
        self.client.force_authenticate(user=self.user)
        data = {"first_name": "Johnny", "bio": "New bio"}
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["first_name"], "Johnny")
        self.assertEqual(response.data["bio"], "New bio")

    def test_update_user_other_profile_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"first_name": "Hacker"}
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, 403)

    def test_update_user_password_updates_hash(self):
        old_hash = self.user.password
        self.client.force_authenticate(user=self.user)
        data = {"password": "newpass5678"}
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.password, old_hash)

    def test_delete_user_own_account_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user.id)

    def test_delete_user_other_account_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(id=self.user.id).exists())
