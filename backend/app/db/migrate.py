from datetime import UTC, datetime
from pathlib import Path

from app.db.database import Database

MIGRATIONS_PATH = Path(__file__).with_name("migrations")


class PendingMigrationsError(RuntimeError):
    pass


def files() -> list[Path]:
    return sorted(MIGRATIONS_PATH.glob("*.sql"))


class Migrator:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def applied(self) -> set[str]:
        async with self._database.cursor() as cursor:
            await cursor.execute("SELECT version FROM schema_migrations")
            return {row["version"] for row in await cursor.fetchall()}

    async def pending(self) -> list[Path]:
        done = await self.applied()
        return [path for path in files() if path.stem not in done]

    async def verify(self) -> None:
        waiting = await self.pending()
        if waiting:
            names = ", ".join(path.stem for path in waiting)
            raise PendingMigrationsError(
                f"Pending migrations: {names}. Run `make migrate` first."
            )

    async def apply(self) -> list[str]:
        now = datetime.now(UTC).isoformat()
        applied = []
        for path in await self.pending():
            async with self._database.cursor() as cursor:
                await cursor.executescript(path.read_text())
                await cursor.execute(
                    "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                    (path.stem, now),
                )
            applied.append(path.stem)
        return applied
