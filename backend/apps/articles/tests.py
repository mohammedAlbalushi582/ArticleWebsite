import pytest
from unittest.mock import patch
from django.test import TestCase
from rest_framework.test import APIClient

from apps.users.models import User
from .models import Article


@pytest.mark.django_db
class TestArticleModel(TestCase):
    def test_create_article_with_user(self):
        user = User.objects.create_user(email="art@example.com", password="pass1234")
        article = Article.objects.create(
            user=user,
            title="Test Article",
            raw_text="Some text content",
            summary="A summary",
            key_points=["point 1", "point 2"],
            tags=["test"],
        )
        assert article.title == "Test Article"
        assert article.user == user
        assert len(article.key_points) == 2

    def test_create_article_with_session(self):
        article = Article.objects.create(
            session_key="test-session-123",
            title="Anonymous Article",
            raw_text="Content",
            summary="Summary",
            key_points=["p1"],
            tags=["t1"],
        )
        assert article.user is None
        assert article.session_key == "test-session-123"


@pytest.mark.django_db
class TestArticleEndpointsAuthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="art2@example.com", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.article = Article.objects.create(
            user=self.user,
            title="Existing Article",
            raw_text="Article content here.",
            summary="Summary here.",
            key_points=["point"],
            tags=["tag"],
        )

    def test_list_articles(self):
        response = self.client.get("/api/articles/")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_retrieve_article(self):
        response = self.client.get(f"/api/articles/{self.article.id}/")
        assert response.status_code == 200
        assert response.json()["title"] == "Existing Article"

    def test_delete_article(self):
        response = self.client.delete(f"/api/articles/{self.article.id}/")
        assert response.status_code == 204
        assert Article.objects.count() == 0


@pytest.mark.django_db
class TestArticleEndpointsAnonymous(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.session_key = "anon-session-abc"
        self.article = Article.objects.create(
            session_key=self.session_key,
            title="Anonymous Article",
            raw_text="Content.",
            summary="Summary.",
            key_points=["p1"],
            tags=["t1"],
        )

    def test_list_articles_by_session(self):
        response = self.client.get("/api/articles/", HTTP_X_SESSION_ID=self.session_key)
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_no_articles_without_session(self):
        response = self.client.get("/api/articles/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    @patch("apps.articles.views.analyze_article")
    def test_analyze_anonymous(self, mock_analyze):
        mock_analyze.return_value = Article.objects.create(
            session_key=self.session_key,
            title="AI Result",
            raw_text="input text",
            summary="AI summary",
            key_points=["p1"],
            tags=["ai"],
        )
        response = self.client.post(
            "/api/articles/analyze/",
            {"text": "Some long article text for analysis."},
            format="json",
            HTTP_X_SESSION_ID=self.session_key,
        )
        assert response.status_code == 201
        assert response.json()["title"] == "AI Result"
