import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from apps.users.models import User
from apps.articles.models import Article
from .models import Highlight


@pytest.mark.django_db
class TestHighlightEndpointsAuthenticated(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="hl@example.com", password="pass1234")
        self.client.force_authenticate(user=self.user)
        self.article = Article.objects.create(
            user=self.user,
            title="Highlight Article",
            raw_text="Content here for highlighting.",
            summary="Summary text",
            key_points=["p1"],
            tags=["t1"],
        )

    def test_create_and_list_highlights(self):
        response = self.client.post(
            f"/api/notes/{self.article.id}/",
            {"text": "Content here", "color": "yellow", "source": "original", "article": self.article.id},
            format="json",
        )
        assert response.status_code == 201
        assert response.json()["text"] == "Content here"

        response = self.client.get(f"/api/notes/{self.article.id}/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_delete_highlight(self):
        hl = Highlight.objects.create(article=self.article, text="To delete", source="summary")
        response = self.client.delete(f"/api/notes/{self.article.id}/{hl.id}/")
        assert response.status_code == 204
        assert Highlight.objects.count() == 0


@pytest.mark.django_db
class TestHighlightEndpointsAnonymous(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.session_key = "hl-session-xyz"
        self.article = Article.objects.create(
            session_key=self.session_key,
            title="Anon HL Article",
            raw_text="Content",
            summary="Summary",
            key_points=["p1"],
            tags=["t1"],
        )

    def test_create_highlight_by_session(self):
        response = self.client.post(
            f"/api/notes/{self.article.id}/",
            {"text": "Session highlight", "color": "green", "source": "summary", "article": self.article.id},
            format="json",
            HTTP_X_SESSION_ID=self.session_key,
        )
        assert response.status_code == 201

    def test_list_highlights_by_session(self):
        Highlight.objects.create(article=self.article, text="Existing", source="summary")
        response = self.client.get(
            f"/api/notes/{self.article.id}/",
            HTTP_X_SESSION_ID=self.session_key,
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
