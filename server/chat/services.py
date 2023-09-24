import asyncio
import hashlib
from typing import AsyncIterable, BinaryIO, Union, Iterator
import magic

from asgiref.sync import sync_to_async
from ninja.errors import ValidationError
from ninja import UploadedFile
from pypdf import PdfReader
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    SpacyTextSplitter,
)
import io
import replicate
from fastapi import HTTPException
from chromadb.api.types import Documents as ChromadbDocuments

from .models import (
    Conversation,
    Message as MessageModel,
    DocumentFile,
    ChromaDBCollection,
)
from .enums import MessageTypeChoices
from .schemas import Message
from .singleton import ChromaDBSingleton

import structlog

logger = structlog.get_logger()

SYSTEM_PROMPT = """System: Use the following pieces of context to answer the users question.
If you don't know the answer, just say that you don't know, don't try to make up an answer."""


async def create_input(messages: list[Message]) -> str:
    """Create the input string for the model.

    :param messages: A list of messages from the user and the system.
    :return: The input string for the model.
    """
    input_string = SYSTEM_PROMPT
    for message in messages:
        input_string += f"\n\n{message.role}: {message.content}"
    return input_string


async def generate_raw_prompt(
    message: str, chat_history: list[tuple[str, str]], system_prompt: str
) -> str:
    """Create the prompt for the model.
    Modified from https://huggingface.co/spaces/huggingface-projects/llama-2-7b-chat/blob/main/model.py#L20

    """
    texts = [f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n"]
    # The first user input is _not_ stripped
    do_strip = False
    for user_input, response in chat_history:
        user_input = user_input.strip() if do_strip else user_input
        do_strip = True
        texts.append(f"{user_input} [/INST] {response.strip()} </s><s>[INST] ")
    message = message.strip() if do_strip else message
    texts.append(f"{message} [/INST]")
    return "".join(texts)


async def get_replicate_stream(
    prompt: str, conversation: Conversation = None
) -> AsyncIterable[str | bytes]:
    collected_output = []

    try:
        # The replicate/llama-2-70b-chat model can stream output as it's running.
        # The predict method returns an iterator, and you can iterate over that output.
        # Prompting guide https://replicate.com/blog/how-to-prompt-llama
        output: Iterator = replicate.run(
            "replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1",
            input={
                "prompt": prompt,
                "system_prompt": "",
            },
        )
        for item in output:
            # Dumb as hell - streaming only works if you introduce a tiny delay
            # Hypothesis
            # The delay essentially serves as a workaround by allowing the client to catch up and request the
            # next chunk of data. It's worth investigating further if there are other underlying issues,
            # such as buffering in your server or any intermediaries, that might affect real-time streaming.
            # print(item)
            collected_output.append(item)
            await asyncio.sleep(0.000001)  # Introducing a delay
            yield item

        if conversation is not None:
            # Save the conversation to the database
            await MessageModel.objects.acreate(
                conversation=conversation,
                message_type=MessageTypeChoices.LLM,
                content="".join(collected_output),
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_pdf_text(pdf_doc: bytes) -> str:
    """
    Extracts text from a given PDF document represented as bytes.

    Args:
        pdf_doc (bytes): The PDF document in bytes format.

    Returns:
        str: The extracted text from the PDF document.

    Raises:
        PdfReadError: If there's an error reading the PDF.

    Examples:
        >>> pdf_path = "path_to_pdf_document.pdf"
        >>> with open(pdf_path, 'rb') as f:
        >>>     pdf_bytes = f.read()
        >>> text = get_pdf_text(pdf_bytes)
        >>> print(text[:100])  # Print the first 100 characters of extracted text.
    """
    text = ""
    pdf_reader = PdfReader(io.BytesIO(pdf_doc))
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text


# Niave splitter that splits on newlines
def simple_splitter(
    text: str, chunk_size: int = 300, chunk_overlap: int = 50
) -> list[str]:
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks


def spacy_splitter(text: str) -> list[str]:
    text_splitter = SpacyTextSplitter()
    return text_splitter.split_text(text)


def recursive_splitter(
    text: str, chunk_size: int = 300, chunk_overlap: int = 50
) -> list[str]:
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", " ", ""],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )

    return text_splitter.split_text(text)


def get_text_chunks(text: str) -> ChromadbDocuments:
    """Splits a given text into chunks of specified size with a specified
    overlap.

    Args:
        text (str): The text to be split into chunks.

    Returns:
        list: A list of text chunks.

    Example:
        >>> text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
        "Sed euismod, urna id aliquet lacinia, nunc nisl ultrices nunc, id lacinia nunc nisl id nisl."
        >>> get_text_chunks(text)
        ['Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed euismod,
        urna id aliquet lacinia, nunc nisl ultrices nunc,', 'id lacinia nunc nisl id nisl.']
    """
    return recursive_splitter(text)


def compute_md5(data: Union[bytes, BinaryIO]) -> str:
    """
    Compute the MD5 hash of the contents of a bytes object or file-like object.

    Args:
        data (Union[bytes, BinaryIO]): A bytes object or file-like object that supports
                                       binary read and seek operations.

    Returns:
        str: The MD5 hash of the contents.
    """

    md5 = hashlib.md5()

    if isinstance(data, bytes):
        md5.update(data)
    else:
        # Read the file in chunks to avoid using too much memory
        for chunk in iter(lambda: data.read(4096), b""):
            md5.update(chunk)

        # Reset the file pointer to its beginning
        data.seek(0)

    return md5.hexdigest()


def delete_conversation(conversation: Conversation):
    client = ChromaDBSingleton().get_client()
    try:
        client.delete_collection(name=str(conversation.collection))
    except Exception as e:
        logger.error("Error deleting collection from ChromaDB", error=str(e))

    conversation.delete()


async def async_delete_conversation(conversation: Conversation):
    await sync_to_async(delete_conversation)(conversation)


def add_unique_document(
    file: Union[BinaryIO, UploadedFile], conversation: Conversation
):
    """Add a new document to a conversation and a vector db collection.
    If an existing one exists, return it instead.
    """

    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file.read(1024))
        file.seek(0)  # reset file pointer to the beginning
    except Exception:
        raise ValidationError(
            errors=[
                {
                    "type": ["file"],
                    "message": "Error detecting file type.",
                }
            ],
        )

    if file_type not in ["application/pdf", "text/plain"]:
        raise ValidationError(
            errors=[
                {
                    "type": ["file"],
                    "message": "Only PDFs and text documents files are supported.",
                }
            ],
        )

    content: bytes = file.read()

    if file_type == "application/pdf":
        text: str = get_pdf_text(content)
    else:
        text: str = content.decode("utf-8")

    md5: str = compute_md5(content)

    existing_file = DocumentFile.objects.filter(
        md5=md5, conversation=conversation
    ).first()

    if existing_file:
        return existing_file

    collection: ChromaDBCollection = ChromaDBSingleton().get_or_create_collection(
        name=str(conversation.collection)
    )

    text_chunks: ChromadbDocuments = get_text_chunks(text)

    logger.info(
        "Adding document to ChromaDB",
        conversation=conversation.uuid,
        text_chunks=text_chunks,
    )

    # Append the md5 to the id to add pseudo uniqueness to uploaded documents.
    collection.add(
        documents=text_chunks,
        ids=[md5 + str(i) for i in range(len(text_chunks))],
        metadatas=[{"md5": md5} for _ in range(len(text_chunks))],
    )

    return DocumentFile.objects.create(
        file=file, md5=md5, conversation=conversation, original_name=file.name
    )


def delete_document(document_file: DocumentFile):
    client = ChromaDBSingleton().get_client()
    try:
        chroma_collection = client.get_collection(
            name=str(document_file.conversation.collection)
        )
        chroma_collection.delete(where={"md5": document_file.md5})
    except Exception as e:
        logger.error("Error deleting document from ChromaDB", error=str(e))

    document_file.delete()
