from collections.abc import AsyncIterator

import httpx
import pytest

from app.api.app import create_app
from app.core.security import PasswordHasher, TokenIssuer
from app.db.chats import ChatRepository
from app.db.database import Database
from app.db.employees import EmployeeRepository
from app.db.seed import Seeder
from app.db.stats import StatsRepository
from app.db.tasks import TaskRepository
from app.services.auth import AuthService
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.stats import StatsService
from app.services.tasks import TaskService

USERNAME = "boss"
PASSWORD = "secret"
BASE_URL = "http://testserver"


@pytest.fixture
async def seeded(database: Database) -> Database:
    await Seeder(database).run()
    return database


@pytest.fixture
async def client(seeded: Database) -> AsyncIterator[httpx.AsyncClient]:
    chats = ChatService(ChatRepository(seeded))
    employees = EmployeeService(EmployeeRepository(seeded))
    application = create_app(
        auth=AuthService(
            username=USERNAME,
            password_hash=PasswordHasher.hash(PASSWORD),
            issuer=TokenIssuer("secret", ttl_minutes=60),
        ),
        tasks=TaskService(
            repository=TaskRepository(seeded), chats=chats, employees=employees
        ),
        stats=StatsService(StatsRepository(seeded), "Asia/Tashkent"),
        employees=employees,
        chats=chats,
    )
    transport = httpx.ASGITransport(app=application)
    async with httpx.AsyncClient(transport=transport, base_url=BASE_URL) as client:
        yield client


@pytest.fixture
async def signed_in(client: httpx.AsyncClient) -> httpx.AsyncClient:
    response = await client.post(
        "/api/auth/login", json={"username": USERNAME, "password": PASSWORD}
    )
    assert response.status_code == 200
    return client
