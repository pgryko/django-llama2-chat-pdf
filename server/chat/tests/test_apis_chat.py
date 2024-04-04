import json

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.test.client import AsyncClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from chat.enums import MessageTypeChoices
from chat.models import Conversation, DocumentFile
from uuid import uuid4


from accounts.models import AccountUser
from chat.tests.data import DATA_PATH

pytestmark = pytest.mark.django_db()

User = get_user_model()


# https://github.com/django/channels/issues/1110
@pytest.mark.asyncio
async def test_set_user_message():
    # Create a Conversation instance for testing
    user: AccountUser = await User.objects.acreate(
        username="testuser", email="test@test.com", password="testpassword"
    )

    client = AsyncClient()
    # Todo: fix this so we use username/password auth
    await sync_to_async(client.force_login)(user)

    conversation = await Conversation.objects.acreate(
        uuid="48b2075f-c360-472a-a65a-03fa9fe3ac34", user=user
    )

    url = reverse("chat-api:set_user_message", args=[conversation.uuid])
    message_data = {
        "role": MessageTypeChoices.USER,
        "content": "Test message content",
    }

    response = await client.post(
        url, data=json.dumps(message_data), content_type="application/json"
    )

    assert response.status_code == 200

    # Fetch the updated conversation from the database
    updated_conversation = await Conversation.objects.aget(uuid=conversation.uuid)
    assert await updated_conversation.messages.acount() == 3

    # Assert that the created message matches the posted message
    created_message = await updated_conversation.messages.order_by("created_at").alast()
    assert created_message.message_type == MessageTypeChoices.CONTEXT
    # assert created_message.content == message_data["content"]


# This test calls an embedding function and might fail or take too long
@pytest.mark.asyncio
async def test_upload_file(async_authenticated_client):
    authenticated_client, user = await async_authenticated_client
    # Setup
    room_uuid = uuid4()
    await Conversation.objects.acreate(uuid=room_uuid, user=user)

    file_path = DATA_PATH / "two_lines_example.pdf"

    file = SimpleUploadedFile(
        name="two_lines_example.pdf",
        content=file_path.read_bytes(),
        content_type="application/octet-stream",
    )

    url = reverse("chat-api:upload_file", args=[str(room_uuid)])
    response = await authenticated_client.post(url, {"file": file}, format="multipart")

    # Validate response status
    assert response.status_code == 200

    # Validate that the DocumentFile was created
    assert await DocumentFile.objects.acount() == 1
    created_file = await DocumentFile.objects.afirst()

    response_data = response.json()

    # Validate response data
    assert response_data[0]["url"] == created_file.file.url
    assert response_data[0]["sha256"] == created_file.sha256

    assert "two_lines_example" in response_data[0]["name"]

    # Attempt to reupload the same file
    file = SimpleUploadedFile(
        name="two_lines_example.pdf",
        content=file_path.read_bytes(),
        content_type="application/octet-stream",
    )

    url = reverse("chat-api:upload_file", args=[str(room_uuid)])
    response = await authenticated_client.post(url, {"file": file}, format="multipart")

    # Validate response status
    assert response.status_code == 200
    # No duplicates
    assert await DocumentFile.objects.acount() == 1


@pytest.mark.asyncio
async def test_get_files(async_authenticated_client):
    authenticated_client, user = await async_authenticated_client

    # Setup
    room_uuid = uuid4()
    room = await Conversation.objects.acreate(uuid=room_uuid, user=user)

    file_path = DATA_PATH / "entropy.pdf"

    file = SimpleUploadedFile(
        file_path.name, file_path.read_bytes(), content_type="application/octet-stream"
    )

    await DocumentFile.objects.acreate(
        file=file,
        sha256="c4d749b9acf8fc78b699a2c6a4b7dfe2",  # Generate the sha256 hash of the file if necessary
        conversation=room,
    )

    # Call the get files endpoint
    url = reverse("chat-api:get_files", args=[str(room_uuid)])
    response = await authenticated_client.get(url)

    # Validate response status
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "entropy" in response.json()[0]["name"]


@pytest.mark.asyncio
async def test_delete_files(async_authenticated_client):
    authenticated_client, user = await async_authenticated_client

    # Setup
    room_uuid = uuid4()
    room = await Conversation.objects.acreate(uuid=room_uuid, user=user)

    file_path = DATA_PATH / "entropy.pdf"

    file = SimpleUploadedFile(
        file_path.name, file_path.read_bytes(), content_type="application/octet-stream"
    )

    document_file = await DocumentFile.objects.acreate(
        file=file,
        sha256="c4d749b9acf8fc78b699a2c6a4b7dfe2",  # Generate the sha256 hash of the file if necessary
        conversation=room,
    )

    # Call the delete files endpoint
    url = reverse(
        "chat-api:delete_files", args=[str(room_uuid), str(document_file.uuid)]
    )
    response = await authenticated_client.delete(url)

    # Validate response status and check the file is deleted
    assert response.status_code == 200

    assert await DocumentFile.objects.filter(uuid=document_file.uuid).aexists() is False
