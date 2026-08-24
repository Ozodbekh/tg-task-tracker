from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import aiosqlite

from app.db.stats import StatsRepository
from app.models.digest import EmployeeDigest
from app.models.filters import DateRange
from app.services.views import to_counts

WEEK = timedelta(days=7)


class DigestService:
    def __init__(self, repository: StatsRepository, timezone: str) -> None:
        self._repository = repository
        self._zone = ZoneInfo(timezone)

    async def weekly(self) -> list[EmployeeDigest]:
        rows = await self._repository.digest(self.current_week())
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

    def current_week(self) -> DateRange:
        now = datetime.now(UTC).astimezone(self._zone)
        monday = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        return DateRange(start=monday, end=monday + WEEK)
