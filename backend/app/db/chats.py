from datetime import datetime

from app.db.database import Database
from app.models.chat import Chat, ChatIdentity


class ChatRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def get_by_telegram_id(self, telegram_id: int) -> Chat | None:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                "SELECT * FROM chats WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
        return Chat(**dict(row)) if row else None

    async def list_all(self) -> list[Chat]:
        async with self._database.cursor() as cursor:
            await cursor.execute("SELECT * FROM chats ORDER BY title, telegram_id")
            rows = await cursor.fetchall()
        return [Chat(**dict(row)) for row in rows]

    async def upsert(self, identity: ChatIdentity, now: datetime) -> Chat:
        async with self._database.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO chats (telegram_id, type, title, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (telegram_id) DO UPDATE SET
                    type = excluded.type,
                    title = excluded.title
                RETURNING *
                """,
                (
                    identity.telegram_id,
                    identity.type,
                    identity.title,
                    now.isoformat(),
                ),
            )
            row = await cursor.fetchone()
        return Chat(**dict(row))
