from unittest.mock import patch

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test.client import Client, AsyncClient

User = get_user_model()


@pytest.fixture
def test_user():
    return User.objects.create_user(
        username="testuser", email="test@test.com", password="testpassword"
    )


@pytest.fixture
def authenticated_client(test_user):
    client = Client()
    client.login(username=test_user.username, password="testpassword")
    return client


@pytest.fixture
async def async_test_user():
    user, _ = await User.objects.aupdate_or_create(
        defaults={"email": "test@test.com", "username": "testuser"},
        password="testpassword",
    )

    return user


@pytest.fixture
async def async_authenticated_client(async_test_user):
    # user = await async_test_user
    client = AsyncClient()
    user = await async_test_user
    await sync_to_async(client.force_login)(user)
    # client.login(username=user.username, password="testpassword")
    return client, user


# Helper function to mock an exception from replicate.run
@pytest.fixture
def mock_replicate_run_exception(*args, **kwargs):
    def _mock_run_exception(*args, **kwargs):
        raise Exception("Some error")

    with patch("replicate.run", _mock_run_exception):
        yield  # This yields control to the test function, keeping the patch in effect


# Helper function to mock the replicate.run behavior
@pytest.fixture
def mock_replicate_run():
    def mock_run(*args, **kwargs):
        yield "item1"
        yield "item2"

    # Patch the replicate.run function to use our mock_run
    with patch("replicate.run", mock_run):
        yield  # This yields control to the test function, keeping the patch in effect
