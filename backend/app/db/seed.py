import asyncio
import random
from datetime import UTC, datetime, timedelta

from app.core.config import settings
from app.db.database import Database
from app.models.task import TaskStatus

EMPLOYEE_NAMES = [
    "Ali Valiyev",
    "Dilnoza Karimova",
    "Bek Tursunov",
    "Malika Yusupova",
    "Sardor Rahimov",
    "Nodira Ismoilova",
]

GROUP_TITLES = ["Sales team", "Development", "Operations"]

TASK_TEXTS = [
    "#task prepare the weekly report",
    "#task call the supplier and confirm the delivery",
    "#task fix the payment page",
    "#task review the new contract",
    "#task update the price list",
    "#task collect feedback from the branch",
    "#task plan the next sprint",
    "#task check the warehouse stock",
]

STATUS_WEIGHTS = [
    (TaskStatus.DONE, 48),
    (TaskStatus.OPEN, 18),
    (TaskStatus.IN_PROGRESS, 15),
    (TaskStatus.ON_HOLD, 7),
    (TaskStatus.BLOCKED, 5),
    (TaskStatus.CANCELLED, 7),
]

TASK_COUNT = 400
UNRESOLVED_COUNT = 12
DAYS_BACK = 400


class Seeder:
    def __init__(self, database: Database, seed: int = 20260814) -> None:
        self._database = database
        self._random = random.Random(seed)
        self._now = datetime.now(UTC)

    async def run(self) -> None:
        await self._clear()
        employees = await self._insert_employees()
        chats = await self._insert_chats(employees)
        await self._insert_tasks(employees, chats)
        await self._insert_unresolved(chats)

    async def _clear(self) -> None:
        async with self._database.cursor() as cursor:
            for table in (
                "task_events",
                "tasks",
                "unresolved_messages",
                "chats",
                "employees",
            ):
                await cursor.execute(f"DELETE FROM {table}")
                await cursor.execute(
                    "DELETE FROM sqlite_sequence WHERE name = ?", (table,)
                )

    async def _insert_employees(self) -> list[tuple[int, int]]:
        created = self._stamp(DAYS_BACK)
        rows = []
        async with self._database.cursor() as cursor:
            for index, name in enumerate(EMPLOYEE_NAMES):
                telegram_id = 500_000 + index
                await cursor.execute(
                    "INSERT INTO employees (telegram_id, name, created_at) "
                    "VALUES (?, ?, ?) RETURNING id",
                    (telegram_id, name, created),
                )
                row = await cursor.fetchone()
                rows.append((row["id"], telegram_id))
        return rows

    async def _insert_chats(
        self, employees: list[tuple[int, int]]
    ) -> list[tuple[int, str]]:
        created = self._stamp(DAYS_BACK)
        chats: list[tuple[int, str]] = []
        async with self._database.cursor() as cursor:
            for index, title in enumerate(GROUP_TITLES):
                await cursor.execute(
                    "INSERT INTO chats (telegram_id, type, title, created_at) "
                    "VALUES (?, ?, ?, ?) RETURNING id",
                    (-1_001_000_000_000 - index, "group", title, created),
                )
                row = await cursor.fetchone()
                chats.append((row["id"], "group"))

            for _, telegram_id in employees:
                await cursor.execute(
                    "INSERT INTO chats (telegram_id, type, title, created_at) "
                    "VALUES (?, ?, ?, ?) RETURNING id",
                    (telegram_id, "private", None, created),
                )
                row = await cursor.fetchone()
                chats.append((row["id"], "private"))
        return chats

    async def _insert_tasks(
        self, employees: list[tuple[int, int]], chats: list[tuple[int, str]]
    ) -> None:
        statuses = [status for status, weight in STATUS_WEIGHTS for _ in range(weight)]

        async with self._database.cursor() as cursor:
            for message_id in range(1, TASK_COUNT + 1):
                employee_id, telegram_id = self._random.choice(employees)
                chat_id, _ = self._random.choice(chats)
                status = self._random.choice(statuses)

                created = self._now - timedelta(
                    days=self._random.uniform(0, DAYS_BACK),
                    hours=self._random.uniform(0, 24),
                )
                started = done = cancelled = None
                if status in (TaskStatus.IN_PROGRESS, TaskStatus.DONE):
                    started = created + timedelta(minutes=self._random.uniform(5, 2880))
                if status is TaskStatus.DONE:
                    done = started + timedelta(hours=self._random.uniform(1, 120))
                if status is TaskStatus.CANCELLED:
                    cancelled = created + timedelta(hours=self._random.uniform(1, 48))

                await cursor.execute(
                    """
                    INSERT INTO tasks (
                        chat_id, message_id, employee_id, text, status,
                        created_at, started_at, done_at, cancelled_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    RETURNING id
                    """,
                    (
                        chat_id,
                        message_id,
                        employee_id,
                        self._random.choice(TASK_TEXTS),
                        status,
                        created.isoformat(),
                        started.isoformat() if started else None,
                        done.isoformat() if done else None,
                        cancelled.isoformat() if cancelled else None,
                    ),
                )
                task_id = (await cursor.fetchone())["id"]

                await self._insert_event(
                    cursor, task_id, TaskStatus.OPEN, 1, message_id, created
                )
                if started:
                    await self._insert_event(
                        cursor,
                        task_id,
                        TaskStatus.IN_PROGRESS,
                        telegram_id,
                        message_id,
                        started,
                    )
                if done:
                    await self._insert_event(
                        cursor, task_id, TaskStatus.DONE, telegram_id, message_id, done
                    )
                if cancelled:
                    await self._insert_event(
                        cursor, task_id, TaskStatus.CANCELLED, 1, message_id, cancelled
                    )
                if status in (TaskStatus.ON_HOLD, TaskStatus.BLOCKED):
                    await self._insert_event(
                        cursor,
                        task_id,
                        status,
                        telegram_id,
                        message_id,
                        created + timedelta(hours=self._random.uniform(1, 72)),
                    )

    async def _insert_unresolved(self, chats: list[tuple[int, str]]) -> None:
        groups = [chat_id for chat_id, kind in chats if kind == "group"]
        async with self._database.cursor() as cursor:
            for index in range(UNRESOLVED_COUNT):
                created = self._now - timedelta(days=self._random.uniform(0, 90))
                await cursor.execute(
                    """
                    INSERT INTO unresolved_messages (
                        chat_id, message_id, text, created_at
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        self._random.choice(groups),
                        900_000 + index,
                        "#task somebody please handle this",
                        created.isoformat(),
                    ),
                )

    @staticmethod
    async def _insert_event(
        cursor: object,
        task_id: int,
        status: TaskStatus,
        actor_id: int,
        message_id: int,
        moment: datetime,
    ) -> None:
        await cursor.execute(
            """
            INSERT INTO task_events (
                task_id, status, actor_id, message_id, text, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (task_id, status, actor_id, message_id, "", moment.isoformat()),
        )

    def _stamp(self, days: int) -> str:
        return (self._now - timedelta(days=days)).isoformat()


async def run() -> None:
    database = Database(settings.db_path)
    await database.connect()
    try:
        await Seeder(database).run()
    finally:
        await database.close()
    print(f"Seeded {TASK_COUNT} tasks into {settings.db_path}")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
