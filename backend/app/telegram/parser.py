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
        found = await self.assignees(message)
        return found[0] if found else None

    async def assignees(self, message: Message) -> list[EmployeeIdentity]:
        if message.is_private:
            identity = self._identity(await message.get_chat())
            return [identity] if identity else []

        users = await self._mentioned(message)
        if not users:
            replied = await self._from_reply(message)
            users = [replied] if replied else []

        found: list[EmployeeIdentity] = []
        seen: set[int] = set()
        for user in users:
            if user.id in seen:
                continue
            seen.add(user.id)
            identity = self._identity(user)
            if identity is not None:
                found.append(identity)
        return found

    async def _mentioned(self, message: Message) -> list[User]:
        users = []
        for entity, text in message.get_entities_text():
            if isinstance(entity, MessageEntityMentionName):
                user = await self._fetch(entity.user_id)
            elif isinstance(entity, MessageEntityMention):
                user = await self._fetch(text.lstrip("@"))
            else:
                continue
            if user is not None:
                users.append(user)
        return users

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
