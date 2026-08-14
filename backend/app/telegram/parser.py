from telethon import TelegramClient
from telethon.tl.custom import Message
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName, User

from app.models.chat import ChatIdentity, ChatType
from app.models.employee import EmployeeIdentity


class MessageParser:
    def __init__(self, client: TelegramClient) -> None:
        self._client = client

    @staticmethod
    async def chat(message: Message) -> ChatIdentity:
        if message.is_private:
            return ChatIdentity(telegram_id=message.chat_id, type=ChatType.PRIVATE)
        entity = await message.get_chat()
        return ChatIdentity(
            telegram_id=message.chat_id,
            type=ChatType.GROUP,
            title=getattr(entity, "title", None),
        )

    async def assignee(self, message: Message) -> EmployeeIdentity | None:
        if message.is_private:
            return self._identity(await message.get_chat())

        user = await self._from_text_mention(message)
        if user is None:
            user = await self._from_username(message)
        if user is None:
            user = await self._from_reply(message)
        return self._identity(user)

    async def _from_text_mention(self, message: Message) -> User | None:
        for entity, _ in message.get_entities_text(MessageEntityMentionName):
            return await self._fetch(entity.user_id)
        return None

    async def _from_username(self, message: Message) -> User | None:
        for _, text in message.get_entities_text(MessageEntityMention):
            return await self._fetch(text.lstrip("@"))
        return None

    @staticmethod
    async def _from_reply(message: Message) -> User | None:
        if message.reply_to_msg_id is None:
            return None
        replied = await message.get_reply_message()
        if replied is None:
            return None
        sender = await replied.get_sender()
        return sender if isinstance(sender, User) else None

    async def _fetch(self, reference: int | str) -> User | None:
        try:
            entity = await self._client.get_entity(reference)
        except ValueError, TypeError:
            return None
        return entity if isinstance(entity, User) else None

    @staticmethod
    def _identity(user: User | None) -> EmployeeIdentity | None:
        if user is None:
            return None
        return EmployeeIdentity(
            telegram_id=user.id, name=MessageParser.display_name(user)
        )

    @staticmethod
    def display_name(user: User) -> str:
        parts = [user.first_name, user.last_name]
        name = " ".join(part for part in parts if part)
        return name or user.username or str(user.id)
