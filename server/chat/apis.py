import uuid
from django.contrib.auth import authenticate, login
from chromadb.api import Documents
from django.http import StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from ninja.security import HttpBearer
from ninja import NinjaAPI, File, UploadedFile
from pydantic import BaseModel

from chat import services

from structlog import get_logger

from .schemas import GetResultMetaNone
from .singleton import ChromaDBSingleton


api = NinjaAPI(
    title="Chat API",
    version="1.0.0",
    urls_namespace="chat-api",
)

logger = get_logger()


@api.get("/chroma/heartbeat")
async def chroma_heartbeat(request) -> int:
    """From chromadb get the current time in nanoseconds since epoch.
    Used to check if the chroma service is alive."""
    client = ChromaDBSingleton().get_client()
    return client.heartbeat()


@api.get("/chroma/{collection}")
async def chroma_get(request, collection: uuid.UUID) -> GetResultMetaNone:
    """Return what's stored in the collection."""
    client = ChromaDBSingleton().get_client()
    collection = client.get_or_create_collection()
    return collection.get()


@api.delete("/chroma/{collection}")
async def chroma_delete(request, collection: uuid.UUID) -> None:
    """Deletes the contents of the collection"""
    client = ChromaDBSingleton().get_client()
    collection = client.get_or_create_collection(name=collection)
    return collection.delete()


# for Nginx proxy_buffering off;
@api.post("/stream_chat/{collection}")
async def stream_chat(
    request, collection: uuid.UUID, chat_input: str
) -> StreamingHttpResponse:
    # Allow a user to have a chat using the data stored in a specific collection.
    response = StreamingHttpResponse(
        streaming_content=services.get_replicate_stream(chat_input),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["Transfer-Encoding"] = "chunked"
    return response


@api.post("/upload/{collection}")
async def upload(request, collection: uuid.UUID, file: UploadedFile = File(...)):
    content: bytes = await file.read()
    md5 = services.compute_md5(content)
    text = services.get_pdf_text(content)
    text_chunks: Documents = services.get_text_chunks(text)
    # Append the md5 to the id to add pseudo uniqueness to uploaded documents.
    # Its annoying that collection does not return info about the documents added (e.g. duplicated added)
    client = ChromaDBSingleton().get_client()
    collection = client.get_or_create_collection(name=collection)
    collection.add(
        documents=text_chunks, ids=[md5 + str(i) for i in range(len(text_chunks))]
    )
