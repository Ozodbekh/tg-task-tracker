from datetime import datetime

import aiosqlite

from app.db.database import Database
from app.db.filters import (
    TASK_SOURCE,
    UNRESOLVED_SOURCE,
    task_clause,
    unresolved_clause,
)
from app.models.filters import DateRange, TaskFilters
from app.models.page import Pagination
from app.models.task import Task, TaskEvent, TaskStatus

VIEW_COLUMNS = """
    t.id, t.text, t.status, t.message_id,
    t.created_at, t.started_at, t.done_at, t.cancelled_at,
    e.id AS employee_id, e.telegram_id AS employee_telegram_id,
    e.name AS employee_name, e.created_at AS employee_created_at,
    c.id AS chat_id, c.telegram_id AS chat_telegram_id,
    c.type AS chat_type, c.title AS chat_title,
    c.created_at AS chat_created_at
"""

VIEW_SOURCE = f"{TASK_SOURCE} JOIN employees e ON e.id = t.employee_id"

SORT_COLUMNS: dict[str, str] = {
    "created_at": "t.created_at ASC",
    "-created_at": "t.created_at DESC",
    "done_at": "t.done_at ASC",
    "-done_at": "t.done_at DESC",
}

STATUS_ORDER = """
    CASE t.status
        WHEN 'open' THEN 0
        WHEN 'in_progress' THEN 1
        WHEN 'on_hold' THEN 2
        WHEN 'blocked' THEN 3
        WHEN 'done' THEN 4
        ELSE 5
    END
"""

STATUS_TIMESTAMP_COLUMN: dict[TaskStatus, str | None] = {
    TaskStatus.OPEN: None,
    TaskStatus.IN_PROGRESS: "started_at",
    TaskStatus.ON_HOLD: None,
    TaskStatus.BLOCKED: None,
    TaskStatus.DONE: "done_at",
    TaskStatus.CANCELLED: "cancelled_at",
}


class TaskRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def get(self, chat_id: int, message_id: int) -> Task | None:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM tasks WHERE chat_id = ? AND message_id = ?",
                (chat_id, message_id),
            )
            row = await cursor.fetchone()
        return Task(**dict(row)) if row else None

    async def upsert(
        self,
        chat_id: int,
        message_id: int,
        employee_id: int,
        text: str,
        now: datetime,
    ) -> Task:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO tasks (
                    chat_id, message_id, employee_id, text, status, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT (chat_id, message_id) DO UPDATE SET
                    employee_id = excluded.employee_id,
                    text = excluded.text,
                    status = CASE
                        WHEN tasks.status = ? THEN ?
                        ELSE tasks.status
                    END,
                    cancelled_at = CASE
                        WHEN tasks.status = ? THEN NULL
                        ELSE tasks.cancelled_at
                    END
                RETURNING *
                """,
                (
                    chat_id,
                    message_id,
                    employee_id,
                    text,
                    TaskStatus.OPEN,
                    now.isoformat(),
                    TaskStatus.CANCELLED,
                    TaskStatus.OPEN,
                    TaskStatus.CANCELLED,
                ),
            )
            row = await cursor.fetchone()
        return Task(**dict(row))

    async def set_status(
        self, task_id: int, status: TaskStatus, now: datetime
    ) -> Task | None:
        column = STATUS_TIMESTAMP_COLUMN[status]
        assignment = f", {column} = ?" if column else ""
        parameters: list[object] = [status]
        if column:
            parameters.append(now.isoformat())
        parameters.append(task_id)

        async with self._database.cursor() as cursor:
            await cursor.execute(
                f"UPDATE tasks SET status = ?{assignment} WHERE id = ? RETURNING *",
                parameters,
            )
            row = await cursor.fetchone()
        return Task(**dict(row)) if row else None

    async def cancel_unfinished(
        self, employee_id: int, actor_id: int, now: datetime
    ) -> int:
        stamp = now.isoformat()
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                UPDATE tasks SET status = ?, cancelled_at = ?
                WHERE employee_id = ? AND status NOT IN (?, ?)
                RETURNING id
                """,
                (
                    TaskStatus.CANCELLED,
                    stamp,
                    employee_id,
                    TaskStatus.DONE,
                    TaskStatus.CANCELLED,
                ),
            )
            identifiers = [row["id"] for row in await cursor.fetchall()]
            if identifiers:
                await cursor.executemany(
                    """
                    INSERT INTO task_events (
                        task_id, status, actor_id, message_id, text, created_at
                    )
                    VALUES (?, ?, ?, 0, '', ?)
                    """,
                    [
                        (task_id, TaskStatus.CANCELLED, actor_id, stamp)
                        for task_id in identifiers
                    ],
                )
        return len(identifiers)

    async def add_event(
        self,
        task_id: int,
        status: TaskStatus,
        actor_id: int,
        message_id: int,
        text: str,
        now: datetime,
    ) -> TaskEvent:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO task_events (
                    task_id, status, actor_id, message_id, text, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                RETURNING *
                """,
                (task_id, status, actor_id, message_id, text, now.isoformat()),
            )
            row = await cursor.fetchone()
        return TaskEvent(**dict(row))

    async def list_views(
        self,
        filters: TaskFilters,
        window: DateRange,
        search: str | None,
        pagination: Pagination,
        sort: str,
    ) -> tuple[list[aiosqlite.Row], int]:
        clause = task_clause(filters, window)
        conditions = clause.sql
        parameters = list(clause.parameters)
        if search:
            conditions += " AND t.text LIKE ? ESCAPE '\\'"
            parameters.append(f"%{self._escape(search)}%")

        async with self._database.cursor() as cursor:
            await cursor.execute(
                f"SELECT COUNT(*) AS total FROM {VIEW_SOURCE} WHERE {conditions}",
                parameters,
            )
            total = int((await cursor.fetchone())["total"])

            await cursor.execute(
                f"""
                SELECT {VIEW_COLUMNS}
                FROM {VIEW_SOURCE}
                WHERE {conditions}
                ORDER BY {SORT_COLUMNS[sort]}, t.id DESC
                LIMIT ? OFFSET ?
                """,
                [*parameters, pagination.page_size, pagination.offset],
            )
            rows = list(await cursor.fetchall())
        return rows, total

    async def for_employee(self, employee_id: int) -> list[aiosqlite.Row]:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                f"""
                SELECT {VIEW_COLUMNS}
                FROM {VIEW_SOURCE}
                WHERE t.employee_id = ?
                ORDER BY {STATUS_ORDER}, t.created_at DESC
                """,
                (employee_id,),
            )
            return list(await cursor.fetchall())

    async def view(self, task_id: int) -> aiosqlite.Row | None:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                f"SELECT {VIEW_COLUMNS} FROM {VIEW_SOURCE} WHERE t.id = ?",
                (task_id,),
            )
            return await cursor.fetchone()

    async def events(self, task_id: int) -> list[aiosqlite.Row]:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                SELECT ev.id, ev.status, ev.message_id, ev.text, ev.created_at,
                    ev.actor_id, e.name AS actor_name
                FROM task_events ev
                LEFT JOIN employees e ON e.telegram_id = ev.actor_id
                WHERE ev.task_id = ?
                ORDER BY ev.id
                """,
                (task_id,),
            )
            return list(await cursor.fetchall())

    async def list_unresolved(
        self, filters: TaskFilters, window: DateRange, pagination: Pagination
    ) -> tuple[list[aiosqlite.Row], int]:
        clause = unresolved_clause(filters, window)

        async with self._database.cursor() as cursor:
            await cursor.execute(
                f"SELECT COUNT(*) AS total FROM {UNRESOLVED_SOURCE} WHERE {clause.sql}",
                clause.parameters,
            )
            total = int((await cursor.fetchone())["total"])

            await cursor.execute(
                f"""
                SELECT u.id, u.message_id, u.text, u.created_at,
                    c.id AS chat_id, c.telegram_id AS chat_telegram_id,
                    c.type AS chat_type, c.title AS chat_title,
                    c.created_at AS chat_created_at
                FROM {UNRESOLVED_SOURCE}
                WHERE {clause.sql}
                ORDER BY u.created_at DESC, u.id DESC
                LIMIT ? OFFSET ?
                """,
                [*clause.parameters, pagination.page_size, pagination.offset],
            )
            rows = list(await cursor.fetchall())
        return rows, total

    @staticmethod
    def _escape(value: str) -> str:
        for character in ("\\", "%", "_"):
            value = value.replace(character, f"\\{character}")
        return value

    async def save_unresolved(
        self, chat_id: int, message_id: int, text: str, now: datetime
    ) -> None:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO unresolved_messages (
                    chat_id, message_id, text, created_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT (chat_id, message_id) DO UPDATE SET
                    text = excluded.text
                """,
                (chat_id, message_id, text, now.isoformat()),
            )
