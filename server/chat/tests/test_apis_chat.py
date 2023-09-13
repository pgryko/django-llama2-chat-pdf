import json

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test.client import AsyncClient
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from chat.models import Conversation, DocumentFile
from uuid import uuid4


from accounts.models import AccountUser
from chat.models import Conversation
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
        "role": "user",
        "content": "Test message content",
    }

    response = await client.post(
        url, data=json.dumps(message_data), content_type="application/json"
    )

    assert response.status_code == 200

    # Fetch the updated conversation from the database
    updated_conversation = await Conversation.objects.aget(uuid=conversation.uuid)
    assert await updated_conversation.messages.acount() == 2

    # Assert that the created message matches the posted message
    created_message = await updated_conversation.messages.order_by("created_at").alast()
    assert created_message.message_type == message_data["role"]
    assert created_message.content == message_data["content"]


# Skip for a couple of reasons:
# 1. Test runs very slowly due to using an embedding via CPU
# 2. ChromaDb is not properly configured for testing, i.e. proper teardown of the database
# 3. We will likely swap out ChromaDb for milvus and use a hosted embedding service (via vllm?)
@pytest.mark.skip(reason="Test too slow")
@pytest.mark.asyncio
async def test_upload_file(async_authenticated_client):
    authenticated_client, user = await async_authenticated_client

    # Setup
    room_uuid = uuid4()
    await Conversation.objects.acreate(uuid=room_uuid, user=user)

    file_path = DATA_PATH / "entropy.pdf"

    file = SimpleUploadedFile(
        name="entropy.pdf",
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
    assert response_data["url"] == created_file.file.url
    assert response_data["md5"] == created_file.md5

    assert response_data["name"] == "uploads/entropy.pdf"
