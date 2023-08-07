import uuid

from chromadb.api import Documents
from django.conf import settings
from django.http import StreamingHttpResponse

from ninja import NinjaAPI, File, UploadedFile
from chat import services

from structlog import get_logger

from .schemas import GetResultMetaNone
from .singleton import ChromaDBSingleton
import httpx

api = NinjaAPI(
    title="Chat API",
    version="1.0.0",
    urls_namespace="chat-api",
    csrf=False,
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

    # client = httpx.AsyncClient()
    #
    # async def get_stream():
    #     async with httpx.AsyncClient(follow_redirects=True) as client:
    #         r = await client.post(
    #             url="https://api.replicate.com/v1/predictions",
    #             json={
    #                 "version": "2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
    #                 "stream": True,
    #                 "input": {"prompt": "Tell me a recipe"},
    #             },
    #             headers={"Authorization": f"Token {settings.REPLICATE_API_TOKEN}"},
    #         )
    #         data = r.json()
    #         logger.debug("get_stream", data=data)
    #         return data["urls"]["stream"]
    #
    # async def stream(url):
    #     async with client.stream(
    #         "GET",
    #         url=url,
    #         headers={"Authorization": f"Token {settings.REPLICATE_API_TOKEN}"},
    #     ) as r:
    #         async for chunk in r.aiter_bytes():
    #             print("chunk", chunk)
    #             yield chunk
    #
    # stream_url = await get_stream()
    # print("stream_url", stream_url)
    # # response = StreamingHttpResponse(
    # #     streaming_content=stream(stream_url),
    # #     content_type="text/event-stream",
    # # )


# for Nginx proxy_buffering off;
@api.get("/stream_chat/{chat_input}")
async def stream_chat(request, chat_input: str) -> StreamingHttpResponse:
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
