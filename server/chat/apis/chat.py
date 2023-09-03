from django.http import StreamingHttpResponse
from ninja import Router
from ninja.params import Form

from structlog import get_logger

import chat.services as services

from pydantic.types import UUID4

logger = get_logger()

router = Router()


# for Nginx proxy_buffering off;
@router.post("stream_chat/{room_uuid}")
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
