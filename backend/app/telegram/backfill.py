import asyncio
import logging
from dataclasses import dataclass

from telethon import TelegramClient
from telethon.tl.custom import Message

from app.models.chat import ChatIdentity
from app.models.task import StatusChange, TaskCapture, TaskStatus, UnresolvedMessage
from app.services.tasks import TaskService
from app.telegram.parser import MessageParser
from app.telegram.tags import TagReader

logger = logging.getLogger(__name__)

SLEEP_EVERY = 40
SLEEP_SECONDS = 1.0


@dataclass
class Report:
    seen: int = 0
    captured: int = 0
    statuses: int = 0
    unresolved: int = 0
    already_stored: int = 0
    foreign_status: int = 0
    multi_assignee: int = 0
    failed: int = 0


class HistoryBackfill:
    def __init__(
        self,
        client: TelegramClient,
        parser: MessageParser,
        tasks: TaskService,
        apply: bool,
    ) -> None:
        self._client = client
        self._parser = parser
        self._tasks = tasks
        self._apply = apply
        self._captured: set[int] = set()

    async def run(self, chat_id: int) -> Report:
        report = Report()
        self._captured = set()
        entity = await self._client.get_entity(chat_id)

        async for message in self._client.iter_messages(entity, reverse=True):
            report.seen += 1
            if report.seen % SLEEP_EVERY == 0:
                await asyncio.sleep(SLEEP_SECONDS)
            try:
                await self._handle(message, report)
            except Exception:
                report.failed += 1
                logger.exception("Failed on message %s", message.id)

        return report

    async def _handle(self, message: Message, report: Report) -> None:
        text = message.text or ""
        if message.out:
            if TagReader.has_task_tag(text):
                await self._capture(message, text, report)
            return
        if message.reply_to_msg_id is None:
            return
        status = TagReader.status(text)
        if status is not None:
            await self._status(message, text, status, report)

    async def _capture(self, message: Message, text: str, report: Report) -> None:
        if message.sender_id is None:
            report.failed += 1
            logger.warning("Message %s has no sender, skipped", message.id)
            return

        chat = await self._parser.chat(message)
        assignees = await self._parser.assignees(message)

        if not assignees:
            report.unresolved += 1
            logger.info("unresolved | %s | %s", message.id, text[:60])
            if self._apply:
                await self._tasks.record_unresolved(
                    UnresolvedMessage(chat=chat, message_id=message.id, text=text),
                    message.date,
                )
            return

        if len(assignees) > 1:
            report.multi_assignee += 1
            logger.warning(
                "message %s mentions %s people (%s); only %s is stored",
                message.id,
                len(assignees),
                ", ".join(person.name for person in assignees),
                assignees[0].name,
            )

        if await self._tasks.find(chat, message.id) is not None:
            report.already_stored += 1
            logger.info("exists     | %s | %s", message.id, text[:60])
            return

        report.captured += 1
        self._captured.add(message.id)
        logger.info(
            "task       | %s | %s | %s | %s",
            message.date,
            message.id,
            assignees[0].name,
            text[:60],
        )
        if self._apply:
            await self._tasks.capture(
                TaskCapture(
                    chat=chat,
                    message_id=message.id,
                    author_id=message.sender_id,
                    assignee=assignees[0],
                    text=text,
                ),
                message.date,
            )

    async def _status(
        self, message: Message, text: str, status: TaskStatus, report: Report
    ) -> None:
        if message.sender_id is None:
            report.failed += 1
            logger.warning("Message %s has no sender, skipped", message.id)
            return

        if message.reply_to_msg_id not in self._captured:
            report.foreign_status += 1
            return

        report.statuses += 1
        logger.info(
            "status     | %s | %s -> %s | %s",
            message.date,
            message.reply_to_msg_id,
            status,
            text[:40],
        )
        if self._apply:
            chat: ChatIdentity = await self._parser.chat(message)
            await self._tasks.apply_status(
                StatusChange(
                    chat=chat,
                    task_message_id=message.reply_to_msg_id,
                    status=status,
                    actor_id=message.sender_id,
                    message_id=message.id,
                    text=text,
                ),
                message.date,
            )
