from datetime import datetime
import uuid
from ninja import Schema
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


class MessageTypeEnum(str, Enum):
    SYS = "system"
    USER = "user"
    CONTEXT = "vectordb"
    LLM = "llm"


class MessageSchema(Schema):
    uuid: uuid.UUID
    message_type: MessageTypeEnum
    content: str
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ChatInput(BaseModel):
    messages: List[Message]


class ChatOutput(BaseModel):
    message: Message
