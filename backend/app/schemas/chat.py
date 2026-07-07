from __future__ import annotations

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.mentor import ResponseLanguage


ChatRole = Literal["user", "assistant"]


class ChatHistoryMessage(BaseModel):
    role: ChatRole
    content: str = Field(min_length=1, max_length=12000)


class ChatStreamRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    chat_id: UUID | None = None
    history: list[ChatHistoryMessage] = Field(default_factory=list, max_length=20)
    language: ResponseLanguage = ResponseLanguage.uz_latin
