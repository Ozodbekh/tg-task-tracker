from collections.abc import AsyncIterator

import httpx
import pytest

from app.api.app import create_app
from app.bot.client import create_bot
from app.bot.handlers import BotHandlers
from app.bot.report import TaskReport
from app.bot.webhook import BotWebhook
from app.core.security import PasswordHasher, TokenIssuer
from app.db.chats import ChatRepository
from app.db.database import Database
from app.db.employees import EmployeeRepository
from app.db.stats import StatsRepository
from app.db.tasks import TaskRepository
from app.services.auth import AuthService
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.staff import StaffService
from app.services.stats import StatsService
from app.services.tasks import TaskService

TOKEN = "123456:AAtestTOKENtestTOKENtestTOKENtestTOK"
SECRET = "webhook-secret"
BASE_URL = "http://testserver"


@pytest.fixture
def handlers(database: Database) -> BotHandlers:
    chats = ChatService(ChatRepository(database))
    employees = EmployeeService(EmployeeRepository(database))
    tasks = TaskService(
        repository=TaskRepository(database), chats=chats, employees=employees
    )
    return BotHandlers(employees, tasks, TaskReport("Asia/Tashkent"))


@pytest.fixture
async def client(
    database: Database, handlers: BotHandlers
) -> AsyncIterator[httpx.AsyncClient]:
    chats = ChatService(ChatRepository(database))
    employees = EmployeeService(EmployeeRepository(database))
    tasks = TaskService(
        repository=TaskRepository(database), chats=chats, employees=employees
    )
    webhook = BotWebhook(create_bot(TOKEN), handlers.dispatcher(), SECRET)

    application = create_app(
        auth=AuthService(
            username="boss",
            password_hash=PasswordHasher.hash("secret"),
            issuer=TokenIssuer("secret", ttl_minutes=60),
        ),
        tasks=tasks,
        stats=StatsService(StatsRepository(database), "Asia/Tashkent"),
        employees=employees,
        chats=chats,
        staff=StaffService(employees, tasks),
        bot_routes=webhook.routes(),
    )

    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as connection:
        yield connection
    await webhook.close()
