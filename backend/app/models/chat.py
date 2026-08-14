from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class ChatType(StrEnum):
    PRIVATE = "private"
    GROUP = "group"


class ChatIdentity(BaseModel):
    telegram_id: int
    type: ChatType
    title: str | None = None


class Chat(BaseModel):
    id: int
    telegram_id: int
    type: ChatType
    title: str | None
    created_at: datetime
