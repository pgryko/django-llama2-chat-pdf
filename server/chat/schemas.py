from datetime import datetime
import uuid
from ninja import Schema
from pydantic import BaseModel
from typing import List, Mapping, Union, Optional, TypedDict
from chromadb.api.types import ID, Embedding, Document
from enum import Enum

from chat.enums import MessageTypeChoices

Metadata_None = Mapping[str, Union[str, int, float, bool, None]]


class GetResultMetaNone(TypedDict):
    ids: List[ID]
    embeddings: Optional[List[Embedding]]
    documents: Optional[List[Document]]
    # Same as GetResult but metadata is allowed to be None
    metadatas: Optional[List[Union[Metadata_None, None]]]


class MessageType(str, Enum):
    USER = MessageTypeChoices.USER
    SYSTEM = MessageTypeChoices.SYSTEM
    CONTEXT = MessageTypeChoices.CONTEXT
    LLM = MessageTypeChoices.LLM


class Message(BaseModel):
    role: MessageType
    content: str


class MessageSchema(Schema):
    uuid: uuid.UUID
    message_type: MessageType
    content: str
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True


class ChatInput(BaseModel):
    messages: List[Message]


class ChatOutput(BaseModel):
    message: Message


class TimeStampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class DocumentFileSchema(TimeStampSchema):
    url: str
    name: str
    sha256: Optional[str]
