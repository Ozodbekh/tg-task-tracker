from datetime import datetime

from app.db.database import Database
from app.models.employee import Employee, EmployeeIdentity


class EmployeeRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def get_by_telegram_id(self, telegram_id: int) -> Employee | None:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM employees WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
        return Employee(**dict(row)) if row else None

    async def get(self, employee_id: int) -> Employee | None:
        async with self._database.cursor() as cursor:
            await cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            row = await cursor.fetchone()
        return Employee(**dict(row)) if row else None

    async def list_all(self) -> list[Employee]:
        async with self._database.cursor() as cursor:
            await cursor.execute("SELECT * FROM employees ORDER BY name")
            rows = await cursor.fetchall()
        return [Employee(**dict(row)) for row in rows]

    async def set_left_at(
        self, employee_id: int, moment: datetime | None
    ) -> Employee | None:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                "UPDATE employees SET left_at = ? WHERE id = ? RETURNING *",
                (moment.isoformat() if moment else None, employee_id),
            )
            row = await cursor.fetchone()
        return Employee(**dict(row)) if row else None

    async def upsert(self, identity: EmployeeIdentity, now: datetime) -> Employee:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO employees (telegram_id, name, created_at)
                VALUES (?, ?, ?)
                ON CONFLICT (telegram_id) DO UPDATE SET
                    name = excluded.name
                RETURNING *
                """,
                (identity.telegram_id, identity.name, now.isoformat()),
            )
            row = await cursor.fetchone()
        return Employee(**dict(row))
