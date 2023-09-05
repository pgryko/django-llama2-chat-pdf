from pydantic import BaseModel
from typing import List, Mapping, Union, Optional, TypedDict
from chromadb.api.types import ID, Embedding, Document
from enum import Enum

Metadata_None = Mapping[str, Union[str, int, float, bool, None]]


class GetResultMetaNone(TypedDict):
    ids: List[ID]
    embeddings: Optional[List[Embedding]]
    documents: Optional[List[Document]]
    # Same as GetResult but metadata is allowed to be None
    metadatas: Optional[List[Union[Metadata_None, None]]]


class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    CONTEXT = "context"


class Message(BaseModel):
    role: Role
    content: str


class ChatInput(BaseModel):
    messages: List[Message]


class ChatOutput(BaseModel):
    message: Message
