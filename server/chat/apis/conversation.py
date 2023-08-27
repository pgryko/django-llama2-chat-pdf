from chromadb.api import Documents
from ninja import File, UploadedFile, Router

from chat import services

from structlog import get_logger

from chat.singleton import ChromaDBSingleton

from pydantic.types import UUID4

router = Router()


logger = get_logger()


@router.post("document/{collection}")
async def upload(request, collection: UUID4, file: UploadedFile = File(...)):
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
