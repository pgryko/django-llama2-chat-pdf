import json

import pytest
from django.urls import reverse
from chat.models import Conversation


pytestmark = pytest.mark.django_db(transaction=True)


# https://github.com/django/channels/issues/1110
@pytest.mark.asyncio
async def test_set_user_message(async_test_user, async_authenticated_client):
    async_authenticated_client = await async_authenticated_client

    # Create a Conversation instance for testing

    conversation = await Conversation.objects.acreate(
        uuid="48b2075f-c360-472a-a65a-03fa9fe3ac34", user=await async_test_user
    )

    url = reverse("chat-api:set_user_message", args=[conversation.uuid])
    message_data = {
        "role": "user",
        "content": "Test message content",
    }

    response = await async_authenticated_client.post(
        url, data=json.dumps(message_data), content_type="application/json"
    )

    assert response.status_code == 200

    # Fetch the updated conversation from the database
    updated_conversation = Conversation.objects.get(uuid=conversation.uuid)
    assert updated_conversation.messages.count() == 1

    # Assert that the created message matches the posted message
    created_message = updated_conversation.messages.first()
    assert created_message.message_type == message_data["role"]
    assert created_message.content == message_data["content"]
