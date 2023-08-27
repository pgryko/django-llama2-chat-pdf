from typing import Sequence
from chromadb.api.models.Collection import Collection
from ninja import Router
from django.http import HttpRequest
from ninja.errors import HttpError

from chat.models import Conversation

from structlog import get_logger

from server.utils import aget_object_or_404
from chat.schemas import GetResultMetaNone
from chat.singleton import ChromaDBSingleton

from pydantic.types import UUID4

logger = get_logger()

router = Router()


@router.get("chroma/heartbeat")
async def chroma_heartbeat(request: HttpRequest) -> int:
    """From chromadb get the current time in nanoseconds since epoch.
    Used to check if the chroma service is alive."""
    # TODO: add an exponential backoff to this
    client = ChromaDBSingleton().get_client()
    return client.heartbeat()


@router.get("chroma/list")
async def list_collections(request) -> Sequence[Collection]:
    """Return a list of all collections."""
    if request.auth.is_superuser:
        client = ChromaDBSingleton().get_client()
        return client.list_collections()
    else:
        raise HttpError(403, message="Only superusers can list collections.")


@router.get("/chroma/{collection}")
async def chroma_get(request, collection: UUID4) -> GetResultMetaNone:
    # Ensure user has access
    if request.auth.is_superuser:
        collection = await aget_object_or_404(Conversation, uuid=collection)
    else:
        collection = await aget_object_or_404(
            Conversation, uuid=collection, user=request.auth
        )

    """Return what's stored in the collection."""
    client = ChromaDBSingleton().get_client()
    try:
        chroma_collection = client.get_collection(name=collection)
    except ValueError:
        raise HttpError(
            404, message=f"Collection {str(collection.uuid)} not found in ChromaDB"
        )
    except Exception as e:
        logger.error(e)
        raise e
    return chroma_collection.get()


@router.delete("/chroma/{collection}")
async def chroma_delete(request, collection: UUID4) -> None:
    """Deletes the contents of the collection"""
    client = ChromaDBSingleton().get_client()
    collection = client.get_or_create_collection(name=collection)
    return collection.delete()
