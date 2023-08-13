# import pytest
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from django.contrib.auth.admin import UserAdmin
# from django.contrib.admin.sites import AdminSite
# from accounts.admin import AccountUserAdmin
# from accounts.models import AccountUser
#
# pytestmark = pytest.mark.django_db
#
#
# def test_admin_user_change_page(client):
#     User = get_user_model()
#     admin_user = User.objects.create_superuser(
#         email="admin@example.com", password="adminpassword"
#     )
#     client.force_login(admin_user)
#     user = User.objects.create_user(email="test@example.com", password="testpassword")
#     url = reverse("admin:accounts_accountuser_change", args=[user.pk])
#     response = client.get(url)
#     assert response.status_code == 200
#
#
# def test_admin_user_changelist_page(client):
#     User = get_user_model()
#     admin_user = User.objects.create_superuser(
#         email="admin@example.com", password="adminpassword"
#     )
#     client.force_login(admin_user)
#     url = reverse("admin:accounts_accountuser_changelist")
#     response = client.get(url)
#     assert response.status_code == 200
