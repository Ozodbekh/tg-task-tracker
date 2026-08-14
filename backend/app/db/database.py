from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import aiosqlite

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


class Database:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self._connection is not None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        connection = await aiosqlite.connect(self._path)
        connection.row_factory = aiosqlite.Row
        await connection.execute("PRAGMA journal_mode = WAL")
        await connection.execute("PRAGMA foreign_keys = ON")
        await connection.executescript(SCHEMA_PATH.read_text())
        await connection.commit()
        self._connection = connection

    async def close(self) -> None:
        if self._connection is None:
            return
        await self._connection.close()
        self._connection = None

    @asynccontextmanager
    async def cursor(self) -> AsyncIterator[aiosqlite.Cursor]:
        if self._connection is None:
            raise RuntimeError("Database is not connected")
        cursor = await self._connection.cursor()
        try:
            yield cursor
            await self._connection.commit()
        except Exception:
            await self._connection.rollback()
            raise
        finally:
            await cursor.close()
