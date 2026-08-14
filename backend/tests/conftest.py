import os
from collections.abc import AsyncIterator
from pathlib import Path

import pytest

os.environ.setdefault("API_ID", "1")
os.environ.setdefault("API_HASH", "test")
os.environ.setdefault("ADMIN_USERNAME", "boss")
os.environ.setdefault("ADMIN_PASSWORD_HASH", "scrypt$00$00")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("COOKIE_SECURE", "false")

from app.db.chats import ChatRepository
from app.db.database import Database
from app.db.employees import EmployeeRepository
from app.db.tasks import TaskRepository
from app.models.chat import ChatIdentity, ChatType
from app.models.employee import EmployeeIdentity
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.tasks import TaskService


@pytest.fixture
async def database(tmp_path: Path) -> AsyncIterator[Database]:
    database = Database(tmp_path / "test.db")
    await database.connect()
    yield database
    await database.close()


@pytest.fixture
def tasks(database: Database) -> TaskService:
    return TaskService(
        repository=TaskRepository(database),
        chats=ChatService(ChatRepository(database)),
        employees=EmployeeService(EmployeeRepository(database)),
    )


@pytest.fixture
def employees(database: Database) -> EmployeeService:
    return EmployeeService(EmployeeRepository(database))


@pytest.fixture
def group() -> ChatIdentity:
    return ChatIdentity(telegram_id=-100, type=ChatType.GROUP, title="Team")


@pytest.fixture
def private() -> ChatIdentity:
    return ChatIdentity(telegram_id=555, type=ChatType.PRIVATE)


@pytest.fixture
def assignee() -> EmployeeIdentity:
    return EmployeeIdentity(telegram_id=777, name="Ali Valiyev")
