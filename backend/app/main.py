import asyncio
import logging

import uvicorn

from app.api.app import create_app
from app.bot.client import create_bot
from app.bot.handlers import BotHandlers
from app.bot.report import TaskReport
from app.bot.webhook import BotWebhook
from app.core.config import settings
from app.core.security import TokenIssuer
from app.db.chats import ChatRepository
from app.db.database import Database
from app.db.employees import EmployeeRepository
from app.db.stats import StatsRepository
from app.db.tasks import TaskRepository
from app.services.auth import AuthService
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.stats import StatsService
from app.services.tasks import TaskService
from app.telegram.client import create_client
from app.telegram.handlers import TaskEventHandler
from app.telegram.parser import MessageParser

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"


def build_auth() -> AuthService:
    return AuthService(
        username=settings.admin_username,
        password_hash=settings.admin_password_hash,
        issuer=TokenIssuer(settings.jwt_secret, settings.jwt_ttl_minutes),
    )


class Services:
    def __init__(self, database: Database) -> None:
        self.chats = ChatService(ChatRepository(database))
        self.employees = EmployeeService(EmployeeRepository(database))
        self.tasks = TaskService(
            repository=TaskRepository(database),
            chats=self.chats,
            employees=self.employees,
        )
        self.stats = StatsService(StatsRepository(database), settings.timezone)
        self.auth = build_auth()


def build_bot(services: Services) -> BotWebhook | None:
    if not settings.bot_token:
        logger.warning("BOT_TOKEN is not set, the bot is disabled")
        return None

    handlers = BotHandlers(
        employees=services.employees,
        tasks=services.tasks,
        report=TaskReport(settings.timezone),
    )
    return BotWebhook(
        create_bot(settings.bot_token),
        handlers.dispatcher(),
        settings.bot_webhook_secret,
    )


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logging.getLogger("telethon").setLevel(logging.WARNING)

    database = Database(settings.db_path)
    await database.connect()

    services = Services(database)

    client = create_client(settings.session_path, settings.api_id, settings.api_hash)
    TaskEventHandler(client, MessageParser(client), services.tasks).register()

    webhook = build_bot(services)

    server = uvicorn.Server(
        uvicorn.Config(
            create_app(
                auth=services.auth,
                tasks=services.tasks,
                stats=services.stats,
                employees=services.employees,
                chats=services.chats,
                bot_routes=webhook.routes() if webhook else (),
            ),
            host=settings.host,
            port=settings.port,
            log_config=None,
        )
    )

    try:
        await client.connect()
        if not await client.is_user_authorized():
            raise RuntimeError("No authorized session. Run `make login` first.")

        logger.info(
            "Listening for task messages on %s:%s", settings.host, settings.port
        )
        await asyncio.gather(client.run_until_disconnected(), server.serve())
    finally:
        if webhook is not None:
            await webhook.close()
        await client.disconnect()
        await database.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
