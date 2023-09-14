from typing import List

from asgiref.sync import sync_to_async
from django.http import StreamingHttpResponse
from ninja import Router, UploadedFile, File

from structlog import get_logger

import chat.services as services

from pydantic.types import UUID4

from chat.models import Conversation, Message, DocumentFile
from chat.enums import MessageTypeChoices
from chat import schemas
from chat.schemas import DocumentFileSchema
from chromadb.api.types import Documents as ChromadbDocuments
from chromadb.api.models import Collection as ChromaDBCollection

from chat.singleton import ChromaDBSingleton
from server.utils import aget_object_or_404

logger = get_logger()

router = Router()


@router.post("/upload/{room_uuid}", response=DocumentFileSchema)
async def upload_file(request, room_uuid: UUID4, file: UploadedFile = File(...)):
    room = await aget_object_or_404(Conversation, uuid=room_uuid)

    content: bytes = file.read()
    md5 = services.compute_md5(content)
    text = services.get_pdf_text(content)
    text_chunks: ChromadbDocuments = services.get_text_chunks(text)

    collection: ChromaDBCollection = ChromaDBSingleton().get_or_create_collection(
        name=str(room.collection)
    )

    # Append the md5 to the id to add pseudo uniqueness to uploaded documents.
    collection.add(
        documents=text_chunks,
        ids=[md5 + str(i) for i in range(len(text_chunks))],
        metadatas=[{"md5": md5} for _ in range(len(text_chunks))],
    )

    created_file = await DocumentFile.objects.acreate(
        file=file, md5=md5, conversation=room
    )

    return DocumentFileSchema(
        created_at=created_file.created_at,
        updated_at=created_file.updated_at,
        url=created_file.file.url,
        md5=created_file.md5,
        name=created_file.file.name,
    )


# for Nginx proxy_buffering off;
# Currently a hack, as I originally started with SSE and then switched to streaming response
@router.get("/stream_chat/{room_uuid}")
async def get_stream_chat(request, room_uuid: UUID4) -> StreamingHttpResponse:
    # Allow a user to have a chat using the data stored in a specific collection.

    conversation = await Conversation.objects.aget(uuid=room_uuid)

    user_message = await (
        Message.objects.filter(
            conversation__uuid=room_uuid, message_type=MessageTypeChoices.USER
        )
        .order_by("created_at")
        .afirst()
    )

    system_message = await (
        Message.objects.filter(
            conversation__uuid=room_uuid, message_type=MessageTypeChoices.SYSTEM
        )
        .order_by("created_at")
        .afirst()
    )

    vector_db_context = await (
        Message.objects.filter(
            conversation__uuid=room_uuid, message_type=MessageTypeChoices.CONTEXT
        )
        .order_by("created_at")
        .afirst()
    )

    if user_message is None:
        raise Exception("No user messages found for this conversation")

    if vector_db_context is not None:
        prompt = f"""<s>[INST] <<SYS>>
                { system_message.content }
                <</SYS>>
                {vector_db_context.content}
                { user_message.content } [/INST]"""

    else:
        prompt = user_message.content

    # await logger.ainfo("Prompt", prompt=prompt, room=room_uuid, msg=prompt)

    response = StreamingHttpResponse(
        streaming_content=services.get_replicate_stream(
            prompt=prompt, conversation=conversation
        ),
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


@sync_to_async()
def query_collection(collection_uuid: str, query: list[str]) -> str:
    collection = ChromaDBSingleton().get_or_create_collection(name=collection_uuid)
    response: list[list] = collection.query(
        query_texts=query,
        n_results=10,
    )["documents"]

    if len(response) > 0:
        return "".join(response[0])


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
        message_type=MessageTypeChoices.SYSTEM,
        content="Use the following pieces of context to answer the users question. If you don't know the answer, "
        "just say that you don't know, don't try to make up an answer.",
    )

    await Message.objects.acreate(
        conversation=conversation,
        message_type=message.role,
        content=message.content,
    )

    vector_db_response = await query_collection(
        str(conversation.collection), [message.content]
    )

    await Message.objects.acreate(
        conversation=conversation,
        message_type=MessageTypeChoices.CONTEXT,
        content=vector_db_response,
    )

    await conversation.arefresh_from_db()

    messages = await sync_to_async(conversation.messages.all)()

    messages_list = await sync_to_async(list)(messages)

    # Convert each instance into a serialized schema
    serialized_messages = [schemas.MessageSchema.from_orm(msg) for msg in messages_list]

    return serialized_messages


@router.get("/messages/{room_uuid}")
async def get_messages(
    request,
    room_uuid: str,
) -> list[schemas.MessageSchema]:
    conversation = await Conversation.objects.aget(uuid=room_uuid)

    messages = await sync_to_async(conversation.messages.all)()

    messages_list = await sync_to_async(list)(messages)

    # Convert each instance into a serialized schema
    serialized_messages = [schemas.MessageSchema.from_orm(msg) for msg in messages_list]

    return serialized_messages
