from datetime import timedelta

import aiosqlite

from app.db.database import Database
from app.db.filters import (
    TASK_SOURCE,
    UNRESOLVED_SOURCE,
    FilterClause,
    task_clause,
    unresolved_clause,
)
from app.models.filters import Bucket, DateRange, TaskFilters
from app.models.page import Pagination

OVERDUE_DAYS = 3

DIGEST_SOURCE = "tasks t JOIN employees e ON e.id = t.employee_id"

COUNT_COLUMNS = """
    COUNT(*) AS total,
    COALESCE(SUM(t.status = 'open'), 0) AS open,
    COALESCE(SUM(t.status = 'in_progress'), 0) AS in_progress,
    COALESCE(SUM(t.status = 'on_hold'), 0) AS on_hold,
    COALESCE(SUM(t.status = 'blocked'), 0) AS blocked,
    COALESCE(SUM(t.status = 'done'), 0) AS done,
    COALESCE(SUM(t.status = 'cancelled'), 0) AS cancelled
"""

DURATION_COLUMNS = """
    AVG(
        CASE WHEN t.done_at IS NOT NULL
        THEN (julianday(t.done_at) - julianday(t.created_at)) * 86400 END
    ) AS avg_completion_seconds,
    AVG(
        CASE WHEN t.started_at IS NOT NULL
        THEN (julianday(t.started_at) - julianday(t.created_at)) * 86400 END
    ) AS avg_response_seconds
"""

BUCKET_EXPRESSION: dict[Bucket, str] = {
    Bucket.HOUR: "strftime('%Y-%m-%dT%H:00:00', t.created_at, ?)",
    Bucket.DAY: "strftime('%Y-%m-%dT00:00:00', t.created_at, ?)",
    Bucket.WEEK: (
        "strftime('%Y-%m-%dT00:00:00', t.created_at, ?, '-6 days', 'weekday 1')"
    ),
    Bucket.MONTH: "strftime('%Y-%m-01T00:00:00', t.created_at, ?)",
}


class StatsRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def totals(self, filters: TaskFilters, window: DateRange) -> aiosqlite.Row:
        clause = task_clause(filters, window)
        overdue_before = (window.end - timedelta(days=OVERDUE_DAYS)).isoformat()
        sql = f"""
            SELECT {COUNT_COLUMNS}, {DURATION_COLUMNS},
                COALESCE(SUM(
                    t.status = 'open'
                    AND datetime(t.created_at) < datetime(?)
                ), 0) AS overdue_open,
                COUNT(DISTINCT t.employee_id) AS active_employees,
                COUNT(DISTINCT t.chat_id) AS active_chats
            FROM {TASK_SOURCE}
            WHERE {clause.sql}
        """
        return await self._fetch_one(sql, [overdue_before, *clause.parameters])

    async def unresolved_total(self, filters: TaskFilters, window: DateRange) -> int:
        clause = unresolved_clause(filters, window)
        row = await self._fetch_one(
            f"SELECT COUNT(*) AS total FROM {UNRESOLVED_SOURCE} WHERE {clause.sql}",
            clause.parameters,
        )
        return int(row["total"])

    async def timeseries(
        self, filters: TaskFilters, window: DateRange, bucket: Bucket, offset: str
    ) -> list[aiosqlite.Row]:
        clause = task_clause(filters, window)
        expression = BUCKET_EXPRESSION[bucket]
        sql = f"""
            SELECT {expression} AS bucket,
                COUNT(*) AS created,
                COALESCE(SUM(t.status = 'done'), 0) AS done,
                COALESCE(SUM(t.status = 'in_progress'), 0) AS in_progress,
                COALESCE(SUM(t.status = 'cancelled'), 0) AS cancelled
            FROM {TASK_SOURCE}
            WHERE {clause.sql}
            GROUP BY bucket
            ORDER BY bucket
        """
        return await self._fetch_all(sql, [offset, *clause.parameters])

    async def by_employee(
        self, filters: TaskFilters, window: DateRange, pagination: Pagination
    ) -> tuple[list[aiosqlite.Row], int]:
        clause = task_clause(filters, window)
        total = await self._count_distinct("t.employee_id", clause)
        sql = f"""
            SELECT e.id, e.telegram_id, e.name, e.created_at,
                {COUNT_COLUMNS}, {DURATION_COLUMNS}
            FROM {TASK_SOURCE}
            JOIN employees e ON e.id = t.employee_id
            WHERE {clause.sql}
            GROUP BY e.id
            ORDER BY total DESC, e.name, e.id
            LIMIT ? OFFSET ?
        """
        rows = await self._fetch_all(
            sql, [*clause.parameters, pagination.page_size, pagination.offset]
        )
        return rows, total

    async def employee_activity(
        self, filters: TaskFilters, window: DateRange
    ) -> dict[int, str]:
        clause = task_clause(filters, window)
        sql = f"""
            SELECT t.employee_id AS employee_id,
                MAX(ev.created_at) AS last_activity_at
            FROM {TASK_SOURCE}
            JOIN task_events ev ON ev.task_id = t.id
            WHERE {clause.sql}
            GROUP BY t.employee_id
        """
        rows = await self._fetch_all(sql, clause.parameters)
        return {row["employee_id"]: row["last_activity_at"] for row in rows}

    async def by_chat(
        self, filters: TaskFilters, window: DateRange, pagination: Pagination
    ) -> tuple[list[aiosqlite.Row], int]:
        clause = task_clause(filters, window)
        total = await self._count_distinct("t.chat_id", clause)
        sql = f"""
            SELECT c.id, c.telegram_id, c.type, c.title, c.created_at,
                {COUNT_COLUMNS},
                COUNT(DISTINCT t.employee_id) AS participants,
                MAX(t.created_at) AS last_task_at
            FROM {TASK_SOURCE}
            WHERE {clause.sql}
            GROUP BY c.id
            ORDER BY total DESC, c.title, c.id
            LIMIT ? OFFSET ?
        """
        rows = await self._fetch_all(
            sql, [*clause.parameters, pagination.page_size, pagination.offset]
        )
        return rows, total

    async def _count_distinct(self, column: str, clause: FilterClause) -> int:
        row = await self._fetch_one(
            f"SELECT COUNT(DISTINCT {column}) AS total "
            f"FROM {TASK_SOURCE} WHERE {clause.sql}",
            clause.parameters,
        )
        return int(row["total"])

    async def unresolved_by_chat(
        self, filters: TaskFilters, window: DateRange
    ) -> dict[int, int]:
        clause = unresolved_clause(filters, window)
        sql = f"""
            SELECT u.chat_id AS chat_id, COUNT(*) AS total
            FROM {UNRESOLVED_SOURCE}
            WHERE {clause.sql}
            GROUP BY u.chat_id
        """
        rows = await self._fetch_all(sql, clause.parameters)
        return {row["chat_id"]: int(row["total"]) for row in rows}

    async def digest(self) -> list[aiosqlite.Row]:
        sql = f"""
            SELECT e.telegram_id, e.name, {COUNT_COLUMNS}
            FROM {DIGEST_SOURCE}
            WHERE e.left_at IS NULL
            GROUP BY e.id
            ORDER BY e.name
        """
        return await self._fetch_all(sql, [])

    async def _fetch_one(self, sql: str, parameters: list[object]) -> aiosqlite.Row:
        async with self._database.cursor() as cursor:
            await cursor.execute(sql, parameters)
            row = await cursor.fetchone()
        return row

    async def _fetch_all(
        self, sql: str, parameters: list[object]
    ) -> list[aiosqlite.Row]:
        async with self._database.cursor() as cursor:
            await cursor.execute(sql, parameters)
            return list(await cursor.fetchall())
