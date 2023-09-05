from typing import List

from django.http import StreamingHttpResponse
from ninja import Router
from ninja.params import Form

from structlog import get_logger

import chat.services as services

from pydantic.types import UUID4

from chat.models import Conversation, Message
from chat import schemas

logger = get_logger()

router = Router()


# for Nginx proxy_buffering off;
@router.post("/stream_chat/{room_uuid}")
# Currently seems like it's not possible to use a SSE with a post request (from the client side)
async def stream_chat(
    request, room_uuid: UUID4, message: str = Form(...)
) -> StreamingHttpResponse:
    # Allow a user to have a chat using the data stored in a specific collection.

    response = StreamingHttpResponse(
        streaming_content=services.get_replicate_stream(message),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["Transfer-Encoding"] = "chunked"
    return response


@router.get("/stream_chat/{room_uuid}")
# Currently seems like it's not possible to use a SSE with a post request (from the client side)
async def get_stream_chat(request, room_uuid: UUID4) -> StreamingHttpResponse:
    # Allow a user to have a chat using the data stored in a specific collection.

    message = (
        Message.objects.filter(conversation__uuid=room_uuid)
        .order_by("-created_at")
        .first()
    )

    if message is None:
        raise Exception("No messages found for this conversation")

    response = StreamingHttpResponse(
        streaming_content=services.get_replicate_stream(message.content),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["Transfer-Encoding"] = "chunked"
    return response


@router.post("/messages/{room_uuid}")
async def set_messages(room_uuid, messages: List[schemas.Message]) -> List[Message]:
    # Not a clean API - used currently for prototyping, so we can set System messages
    # and prompts from the client side.
    # There's also no strict ordering of messages - i.e. a system message can come after a user message.
    conversation = Conversation.objects.get(uuid=room_uuid)

    for message in messages:
        Message.objects.create(
            conversation=conversation,
            message_type=message.role,
            content=message.content,
        )

    return conversation.messages.all()


@router.post("/message/{room_uuid}")
async def set_user_message(room_uuid: str, message: schemas.Message) -> schemas.Message:
    # Not a clean API - used currently for prototyping, so we can set System messages
    # and prompts from the client side.
    # There's also no strict ordering of messages - i.e. a system message can come after a user message.
    conversation = Conversation.objects.get(uuid=room_uuid)

    conversation.messages.all().delete()

    # Message.objects.create(
    #     conversation=conversation,
    #     message_type=message.role,
    #     content=system_prompt,
    # )

    Message.objects.create(
        conversation=conversation,
        message_type=message.role,
        content=message.content,
    )

    return conversation.messages.all()
