from django.test import TestCase
from ninja_jwt.tokens import AccessToken
from rest_framework.test import APIClient

from src.articles.models import Article
from src.comments.models import Comment
from src.users.models import User


class CommentsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="commenter", email="c@example.com", password="pass1234"
        )
        self.other_user = User.objects.create_user(
            username="other", email="o@example.com", password="pass1234"
        )
        self.article = Article.objects.create(
            title="For Comments", content="Content", author=self.user
        )
        self.comment = Comment.objects.create(
            article=self.article, author=self.user, content="Nice!"
        )

        token = AccessToken.for_user(self.user)
        self.auth_headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        self.list_url = "/api/v1/comments/"
        self.detail_url = f"/api/v1/comments/{self.comment.id}"

    def test_list_comments_success(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["content"], "Nice!")

    def test_retrieve_comment_success(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Nice!")

    def test_create_comment_authenticated_success(self):
        data = {"content": "Great post!", "article_id": self.article.id}
        response = self.client.post(
            self.list_url, data, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Great post!")
        self.assertEqual(Comment.objects.count(), 2)

    def test_create_comment_missing_article_fails(self):
        data = {"content": "No article ID"}
        response = self.client.post(
            self.list_url, data, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, 422)

    def test_create_comment_unauthenticated_forbidden(self):
        data = {"content": "No auth", "article_id": self.article.id}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_comment_owner_success(self):
        data = {"content": "Edited"}
        response = self.client.put(
            self.detail_url, data, format="json", **self.auth_headers
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["content"], "Edited")

    def test_update_comment_non_owner_forbidden(self):
        other_token = AccessToken.for_user(self.other_user)
        other_headers = {"HTTP_AUTHORIZATION": f"Bearer {other_token}"}

        data = {"content": "Hijack"}
        response = self.client.put(
            self.detail_url, data, format="json", **other_headers
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_comment_owner_success(self):
        response = self.client.delete(self.detail_url, **self.auth_headers)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_non_owner_forbidden(self):
        other_token = AccessToken.for_user(self.other_user)
        other_headers = {"HTTP_AUTHORIZATION": f"Bearer {other_token}"}

        response = self.client.delete(self.detail_url, **other_headers)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
