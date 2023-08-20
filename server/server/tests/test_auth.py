import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def client():
    return Client()


def test_login_user_valid_credentials(client, user):
    url = reverse("auth-api:login_user")
    response = client.post(
        url,
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Logged in successfully"


def test_login_user_invalid_credentials(client):
    url = reverse("auth-api:login_user")
    response = client.post(
        url,
        data=json.dumps({"username": "testuser", "password": "testpass"}),
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Invalid credentials"


def test_logout_user(client, user):
    client.login(username="testuser", password="testpass")
    url = reverse("auth-api:logout_user")

    response = client.post(url)
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out successfully"
    # Test that the user is actually logged out
    response = client.post(url)

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
