# tests/test_articles.py
from django.test import TestCase
from rest_framework.test import APIClient

from src.articles.models import Article
from src.users.models import User


class ArticlesAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="author", email="a@example.com", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            username="other", email="o@example.com", password="pass1234"
        )
        self.article = Article.objects.create(
            title="Original Title",
            content="Original Content",
            author=self.user,
        )

        self.list_url = "/api/v1/articles/"
        self.detail_url = f"/api/v1/articles/{self.article.id}/"

    def test_list_articles_success(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Original Title")

    def test_retrieve_article_success(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Original Title")

    def test_create_article_authenticated_success(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "New Article", "content": "New Content"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "New Article")
        self.assertEqual(Article.objects.count(), 2)

    def test_create_article_unauthenticated_forbidden(self):
        data = {"title": "No Auth", "content": "Should fail"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, 403)

    def test_update_article_owner_success(self):
        self.client.force_authenticate(user=self.user)
        data = {"title": "Updated Title"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Updated Title")
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated Title")

    def test_update_article_non_owner_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        data = {"title": "Hacked!"}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, 403)

    def test_delete_article_owner_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Article.objects.filter(id=self.article.id).exists())

    def test_delete_article_non_owner_forbidden(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Article.objects.filter(id=self.article.id).exists())
