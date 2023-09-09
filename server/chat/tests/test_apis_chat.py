import json

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test.client import AsyncClient


from accounts.models import AccountUser
from chat.models import Conversation


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
    assert await updated_conversation.messages.acount() == 1

    # Assert that the created message matches the posted message
    created_message = await updated_conversation.messages.afirst()
    assert created_message.message_type == message_data["role"]
    assert created_message.content == message_data["content"]
