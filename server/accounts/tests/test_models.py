import pytest
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


def test_create_user():
    user_model = get_user_model()
    user = user_model.objects.create_user(
        email="test@example.com", password="testpassword", username="test"
    )
    assert user.email == "test@example.com"
    assert user.check_password("testpassword")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


def test_create_superuser():
    user_model = get_user_model()
    user = user_model.objects.create_superuser(
        email="admin@example.com", password="adminpassword", username="test"
    )
    assert user.email == "admin@example.com"
    assert user.check_password("adminpassword")
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser
