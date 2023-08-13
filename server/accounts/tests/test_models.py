import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


def test_create_user():
    User = get_user_model()
    user = User.objects.create_user(email="test@example.com", password="testpassword")
    assert user.email == "test@example.com"
    assert user.check_password("testpassword")
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser


def test_create_superuser():
    User = get_user_model()
    user = User.objects.create_superuser(
        email="admin@example.com", password="adminpassword"
    )
    assert user.email == "admin@example.com"
    assert user.check_password("adminpassword")
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser
