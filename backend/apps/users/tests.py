import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from .models import User


@pytest.mark.django_db
class TestUserModel(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email="test@example.com", password="testpass123", name="Test")
        assert user.email == "test@example.com"
        assert user.name == "Test"
        assert user.check_password("testpass123")

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="testpass123")

    def test_create_superuser(self):
        user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
        assert user.is_staff
        assert user.is_superuser


@pytest.mark.django_db
class TestAuthEndpoints(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register(self):
        response = self.client.post("/api/auth/register/", {
            "email": "new@example.com",
            "name": "New User",
            "password": "newpass123",
        }, format="json")
        assert response.status_code == 201
        assert "tokens" in response.json()
        assert response.json()["user"]["email"] == "new@example.com"

    def test_register_duplicate_email(self):
        User.objects.create_user(email="dup@example.com", password="pass1234")
        response = self.client.post("/api/auth/register/", {
            "email": "dup@example.com",
            "name": "Dup",
            "password": "pass1234",
        }, format="json")
        assert response.status_code == 400

    def test_login(self):
        User.objects.create_user(email="login@example.com", password="loginpass1")
        response = self.client.post("/api/auth/login/", {
            "email": "login@example.com",
            "password": "loginpass1",
        }, format="json")
        assert response.status_code == 200
        assert "access" in response.json()
