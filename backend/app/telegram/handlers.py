import logging

from telethon import TelegramClient, events
from telethon.tl.custom import Message

from app.models.task import StatusChange, TaskCapture, UnresolvedMessage
from app.services.tasks import TaskService
from app.telegram.parser import MessageParser
from app.telegram.tags import TagReader

logger = logging.getLogger(__name__)


class TaskEventHandler:
    def __init__(
        self, client: TelegramClient, parser: MessageParser, tasks: TaskService
    ) -> None:
        self._client = client
        self._parser = parser
        self._tasks = tasks

    def register(self) -> None:
        self._client.add_event_handler(self._on_new_message, events.NewMessage())
        self._client.add_event_handler(self._on_edited_message, events.MessageEdited())

    async def _on_new_message(self, event: events.NewMessage.Event) -> None:
        await self._handle(event.message, edited=False)

    async def _on_edited_message(self, event: events.MessageEdited.Event) -> None:
        await self._handle(event.message, edited=True)

    async def _handle(self, message: Message, edited: bool) -> None:
        try:
            if message.out:
                if TagReader.has_task_tag(message.text or ""):
                    await self._capture(message)
                elif edited:
                    await self._cancel(message)
                return
            await self._apply_status(message)
        except Exception:
            logger.exception(
                "Failed to handle message %s in chat %s",
                message.id,
                message.chat_id,
            )

    async def _capture(self, message: Message) -> None:
        chat = await self._parser.chat(message)
        assignee = await self._parser.assignee(message)
        text = message.text or ""

        if assignee is None:
            await self._tasks.record_unresolved(
                UnresolvedMessage(chat=chat, message_id=message.id, text=text)
            )
            logger.info(
                "Unresolved assignee for message %s in chat %s",
                message.id,
                chat.telegram_id,
            )
            return

        task = await self._tasks.capture(
            TaskCapture(
                chat=chat,
                message_id=message.id,
                author_id=message.sender_id,
                assignee=assignee,
                text=text,
            )
        )
        logger.info(
            "Task %s assigned to %s (%s) in chat %s: %s",
            task.id,
            assignee.name,
            assignee.telegram_id,
            chat.title or chat.telegram_id,
            text,
        )

    async def _cancel(self, message: Message) -> None:
        chat = await self._parser.chat(message)
        task = await self._tasks.cancel(chat, message.id, message.sender_id)
        if task is not None:
            logger.info("Cancelled task %s in chat %s", task.id, chat.telegram_id)

    async def _apply_status(self, message: Message) -> None:
        if message.reply_to_msg_id is None:
            return
        status = TagReader.status(message.text or "")
        if status is None:
            return

        chat = await self._parser.chat(message)
        task = await self._tasks.apply_status(
            StatusChange(
                chat=chat,
                task_message_id=message.reply_to_msg_id,
                status=status,
                actor_id=message.sender_id,
                message_id=message.id,
                text=message.text or "",
            )
        )
        if task is None:
            logger.info(
                "Rejected status %s from user %s in chat %s",
                status,
                message.sender_id,
                chat.telegram_id,
            )
            return
        logger.info("Task %s moved to %s", task.id, task.status)
