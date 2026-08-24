import aiosqlite

from app.db.stats import StatsRepository
from app.models.digest import EmployeeDigest
from app.services.views import to_counts


class DigestService:
    def __init__(self, repository: StatsRepository) -> None:
        self._repository = repository

    async def pending(self) -> list[EmployeeDigest]:
        rows = await self._repository.digest()
        return [
            digest
            for digest in (self._to_digest(row) for row in rows)
            if digest.by_status.done < digest.total
        ]

    @staticmethod
    def _to_digest(row: aiosqlite.Row) -> EmployeeDigest:
        return EmployeeDigest(
            telegram_id=row["telegram_id"],
            name=row["name"],
            total=int(row["total"]),
            by_status=to_counts(row),
        )
