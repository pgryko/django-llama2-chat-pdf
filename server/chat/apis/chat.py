from typing import List

from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse
from ninja import Router, UploadedFile, File

from structlog import get_logger

import chat.services as services

from pydantic.types import UUID4

from chat.models import Conversation, Message, DocumentFile
from chat import schemas
from chat.schemas import DocumentFileSchema
from server.utils import aget_object_or_404

logger = get_logger()

router = Router()


# for Nginx proxy_buffering off;
# @router.post("/stream_chat/{room_uuid}")
# # Currently seems like it's not possible to use a SSE with a post request (from the client side)
# async def stream_chat(
#     request, room_uuid: UUID4, message: str = Form(...)
# ) -> StreamingHttpResponse:
#     # Allow a user to have a chat using the data stored in a specific collection.
#
#     response = StreamingHttpResponse(
#         streaming_content=services.get_replicate_stream(message),
#         content_type="text/event-stream",
#     )
#     response["Cache-Control"] = "no-cache"
#     response["Transfer-Encoding"] = "chunked"
#     return response


@router.post("/upload/{room_uuid}", response=DocumentFileSchema)
async def upload_file(request, room_uuid: UUID4, file: UploadedFile = File(...)):
    room = await aget_object_or_404(Conversation, uuid=room_uuid)

    created_file = await DocumentFile.objects.acreate(file=file, conversation=room)

    return DocumentFileSchema(
        created_at=created_file.created_at,
        updated_at=created_file.updated_at,
        url=created_file.file.url,
        md5=created_file.md5,
        name=created_file.file.name,
    )


@router.get("/stream_chat/{room_uuid}")
# Currently seems like it's not possible to use a SSE with a post request (from the client side)
# Hence we set message/messages via set_user_message and then run a get via this endpoint.
async def get_stream_chat(request, room_uuid: UUID4) -> StreamingHttpResponse:
    # Allow a user to have a chat using the data stored in a specific collection.

    message = await (
        Message.objects.filter(conversation__uuid=room_uuid, message_type="user")
        .order_by("created_at")
        .afirst()
    )

    if message is None:
        raise Exception("No user messages found for this conversation")

    response = StreamingHttpResponse(
        streaming_content=services.get_replicate_stream(message.content),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["Transfer-Encoding"] = "chunked"
    return response


@router.post("/messages/{room_uuid}")
async def set_messages(
    request, room_uuid, messages: List[schemas.Message]
) -> List[Message]:
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
async def set_user_message(
    request, room_uuid: str, message: schemas.Message
) -> list[schemas.MessageSchema]:
    # Not a clean API - used currently for prototyping, so we can set System messages
    # and prompts from the client side.
    # There's also no strict ordering of messages - i.e. a system message can come after a user message.

    conversation = await Conversation.objects.aget(uuid=room_uuid)

    await conversation.messages.all().adelete()

    await Message.objects.acreate(
        conversation=conversation,
        message_type="system",
        content="Use the following pieces of context to answer the users question. If you don't know the answer, "
        "just say that you don't know, don't try to make up an answer.",
    )

    await Message.objects.acreate(
        conversation=conversation,
        message_type=message.role,
        content=message.content,
    )

    await conversation.arefresh_from_db()

    messages = await sync_to_async(conversation.messages.all)()

    messages_list = await sync_to_async(list)(messages)

    # Convert each instance into a serialized schema
    serialized_messages = [schemas.MessageSchema.from_orm(msg) for msg in messages_list]

    return serialized_messages
