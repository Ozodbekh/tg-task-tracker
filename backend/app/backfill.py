import asyncio
import logging
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from app.core.config import settings
from app.db.chats import ChatRepository
from app.db.database import Database
from app.db.employees import EmployeeRepository
from app.db.migrate import Migrator
from app.db.tasks import TaskRepository
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.tasks import TaskService
from app.telegram.backfill import HistoryBackfill
from app.telegram.client import clone_session, create_client
from app.telegram.parser import MessageParser

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"
APPLY_FLAG = "--apply"
USAGE = f"usage: python -m app.backfill <chat_id> [{APPLY_FLAG}]"


async def run(chat_id: int, apply: bool) -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logger.info("Backfill of chat %s, %s", chat_id, "writing" if apply else "dry run")

    database = Database(settings.db_path)
    await database.connect()
    await Migrator(database).verify()

    chats = ChatService(ChatRepository(database))
    employees = EmployeeService(EmployeeRepository(database))
    tasks = TaskService(
        repository=TaskRepository(database), chats=chats, employees=employees
    )

    with TemporaryDirectory() as directory:
        session = Path(directory) / settings.session_path.name
        await clone_session(settings.session_path, session)
        client = create_client(session, settings.api_id, settings.api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                raise RuntimeError("No authorized session. Run `make login` first.")

            backfill = HistoryBackfill(client, MessageParser(client), tasks, apply)
            report = await backfill.run(chat_id)
            logger.info("Read %s messages", report.seen)
            logger.info("  new tasks        %s", report.captured)
            logger.info("  status replies   %s", report.statuses)
            logger.info("  unresolved       %s", report.unresolved)
            logger.info("  already stored   %s", report.already_stored)
            logger.info("  statuses skipped %s", report.foreign_status)
            logger.info("  several assignees %s", report.multi_assignee)
            logger.info("  failed           %s", report.failed)
            if not apply:
                logger.info(
                    "Nothing was written. Repeat with %s to store it.", APPLY_FLAG
                )
        finally:
            await client.disconnect()
            await database.close()


def main() -> None:
    arguments = sys.argv[1:]
    if not arguments:
        raise SystemExit(USAGE)

    apply = APPLY_FLAG in arguments
    identifiers = [argument for argument in arguments if argument != APPLY_FLAG]
    if len(identifiers) != 1:
        raise SystemExit(USAGE)

    try:
        chat_id = int(identifiers[0])
    except ValueError:
        raise SystemExit(USAGE) from None

    asyncio.run(run(chat_id, apply))


if __name__ == "__main__":
    main()
