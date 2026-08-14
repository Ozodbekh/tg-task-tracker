from datetime import UTC, datetime

from app.db.chats import ChatRepository
from app.models.chat import Chat, ChatIdentity


class ChatService:
    def __init__(self, repository: ChatRepository) -> None:
        self._repository = repository

    async def ensure(self, identity: ChatIdentity) -> Chat:
        return await self._repository.upsert(identity, datetime.now(UTC))

    async def find(self, telegram_id: int) -> Chat | None:
        return await self._repository.get_by_telegram_id(telegram_id)

    async def list_all(self) -> list[Chat]:
        return await self._repository.list_all()
