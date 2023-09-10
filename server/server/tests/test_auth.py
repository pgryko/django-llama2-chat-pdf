import json

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client
from django.contrib.auth.hashers import make_password

User = get_user_model()

pytestmark = pytest.mark.django_db


@pytest.fixture
def user2():
    # TODO: there is a flaw where a testuser is already created in the database
    # Possibly due to a conftest in another app?
    return User.objects.get_or_create(
        username="testuser2", defaults={"password": make_password("testpass")}
    )


@pytest.fixture
def client():
    return Client()


def test_login_user_valid_credentials(client, user2):
    url = reverse("auth-api:login_user")

    response = client.post(
        url,
        data=json.dumps({"username": "testuser2", "password": "testpass"}),
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json()["detail"] == "Logged in successfully"


def test_login_user_invalid_credentials(client, user2):
    url = reverse("auth-api:login_user")
    response = client.post(
        url,
        data=json.dumps({"username": "testuser2", "password": "testpasswrong"}),
        content_type="application/json",
    )

    assert response.status_code == 401
    assert response.json()["error"] == "Invalid credentials"


def test_logout_user(client, user2):
    client.login(username="testuser2", password="testpass")
    url = reverse("auth-api:logout_user")

    response = client.post(url)
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out successfully"
    # Test that the user is actually logged out
    response = client.post(url)

    assert response.status_code == 401
    assert response.json()["detail"] == "Unauthorized"
