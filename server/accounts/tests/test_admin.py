import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_admin_user_change_page(client):
    User = get_user_model()
    admin_user = User.objects.create_superuser(
        email="admin@example.com", password="adminpassword", username="admin"
    )
    client.force_login(admin_user)
    user = User.objects.create_user(
        email="test@example.com", password="testpassword", username="test"
    )
    url = reverse("admin:accounts_accountuser_change", args=[user.pk])
    response = client.get(url)
    assert response.status_code == 200


def test_admin_user_changelist_page(client):
    User = get_user_model()
    admin_user = User.objects.create_superuser(
        email="admin@example.com", password="adminpassword", username="admin"
    )
    client.force_login(admin_user)
    url = reverse("admin:accounts_accountuser_changelist")
    response = client.get(url)
    assert response.status_code == 200
