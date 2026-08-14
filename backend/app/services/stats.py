from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.db.stats import StatsRepository
from app.models.chat import Chat
from app.models.employee import Employee
from app.models.filters import Bucket, DateRange, TaskFilters
from app.models.page import Page, Pagination
from app.models.stats import (
    ChatStats,
    EmployeeStats,
    Overview,
    PreviousWindow,
    TimeseriesPoint,
)
from app.services.views import completion_rate, to_counts

BUCKET_KEY_FORMAT = "%Y-%m-%dT%H:%M:%S"


class StatsService:
    def __init__(self, repository: StatsRepository, timezone: str) -> None:
        self._repository = repository
        self._zone = ZoneInfo(timezone)

    async def overview(self, filters: TaskFilters) -> Overview:
        window = filters.range()
        row = await self._repository.totals(filters, window)
        counts = to_counts(row)
        total = int(row["total"])

        return Overview(
            total=total,
            by_status=counts,
            completion_rate=completion_rate(counts, total),
            avg_completion_seconds=row["avg_completion_seconds"],
            avg_response_seconds=row["avg_response_seconds"],
            overdue_open=int(row["overdue_open"]),
            unresolved=await self._repository.unresolved_total(filters, window),
            active_employees=int(row["active_employees"]),
            active_chats=int(row["active_chats"]),
            previous=await self._previous(filters, window),
        )

    async def timeseries(self, filters: TaskFilters) -> list[TimeseriesPoint]:
        window = filters.range()
        bucket = filters.resolved_bucket()
        rows = await self._repository.timeseries(
            filters, window, bucket, self._offset()
        )
        indexed = {row["bucket"]: row for row in rows}

        start = self._start_of(window, indexed)
        if start is None:
            return []

        points = []
        for moment in self._walk(start, self._to_local(window.end), bucket):
            row = indexed.get(moment.strftime(BUCKET_KEY_FORMAT))
            points.append(
                TimeseriesPoint(
                    bucket=moment,
                    created=int(row["created"]) if row else 0,
                    done=int(row["done"]) if row else 0,
                    in_progress=int(row["in_progress"]) if row else 0,
                    cancelled=int(row["cancelled"]) if row else 0,
                )
            )
        return points

    async def by_employee(
        self, filters: TaskFilters, pagination: Pagination
    ) -> Page[EmployeeStats]:
        window = filters.range()
        rows, total = await self._repository.by_employee(filters, window, pagination)
        activity = await self._repository.employee_activity(filters, window)

        items = [
            EmployeeStats(
                employee=Employee(
                    id=row["id"],
                    telegram_id=row["telegram_id"],
                    name=row["name"],
                    created_at=row["created_at"],
                ),
                total=int(row["total"]),
                by_status=to_counts(row),
                completion_rate=completion_rate(to_counts(row), int(row["total"])),
                avg_completion_seconds=row["avg_completion_seconds"],
                avg_response_seconds=row["avg_response_seconds"],
                last_activity_at=activity.get(row["id"]),
            )
            for row in rows
        ]
        return self._page(items, total, pagination)

    async def for_employee(
        self, filters: TaskFilters, employee_id: int
    ) -> EmployeeStats | None:
        scoped = filters.model_copy(update={"employee_id": employee_id})
        page = await self.by_employee(scoped, Pagination(page=1, page_size=1))
        return page.items[0] if page.items else None

    async def by_chat(
        self, filters: TaskFilters, pagination: Pagination
    ) -> Page[ChatStats]:
        window = filters.range()
        rows, total = await self._repository.by_chat(filters, window, pagination)
        unresolved = await self._repository.unresolved_by_chat(filters, window)

        items = [
            ChatStats(
                chat=Chat(
                    id=row["id"],
                    telegram_id=row["telegram_id"],
                    type=row["type"],
                    title=row["title"],
                    created_at=row["created_at"],
                ),
                total=int(row["total"]),
                by_status=to_counts(row),
                completion_rate=completion_rate(to_counts(row), int(row["total"])),
                unresolved=unresolved.get(row["id"], 0),
                participants=int(row["participants"]),
                last_task_at=row["last_task_at"],
            )
            for row in rows
        ]
        return self._page(items, total, pagination)

    @staticmethod
    def _page[T](items: list[T], total: int, pagination: Pagination) -> Page[T]:
        return Page(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def _previous(
        self, filters: TaskFilters, window: DateRange
    ) -> PreviousWindow | None:
        shifted = window.shifted()
        if shifted is None:
            return None

        row = await self._repository.totals(filters, shifted)
        counts = to_counts(row)
        total = int(row["total"])
        return PreviousWindow(
            total=total,
            done=counts.done,
            completion_rate=completion_rate(counts, total),
        )

    def _offset(self) -> str:
        offset = self._zone.utcoffset(datetime.now(UTC)) or timedelta()
        return f"{int(offset.total_seconds() // 60)} minutes"

    def _to_local(self, moment: datetime) -> datetime:
        return moment.astimezone(self._zone)

    def _start_of(
        self, window: DateRange, indexed: dict[str, object]
    ) -> datetime | None:
        if window.start is not None:
            return self._to_local(window.start)
        if not indexed:
            return None
        return datetime.strptime(min(indexed), BUCKET_KEY_FORMAT).replace(
            tzinfo=self._zone
        )

    def _walk(
        self, start: datetime, end: datetime, bucket: Bucket
    ) -> Iterator[datetime]:
        current = self._align(start, bucket)
        while current <= end:
            yield current
            current = self._advance(current, bucket)

    @staticmethod
    def _align(moment: datetime, bucket: Bucket) -> datetime:
        floored = moment.replace(minute=0, second=0, microsecond=0)
        if bucket is Bucket.HOUR:
            return floored
        midnight = floored.replace(hour=0)
        if bucket is Bucket.DAY:
            return midnight
        if bucket is Bucket.WEEK:
            return midnight - timedelta(days=midnight.weekday())
        return midnight.replace(day=1)

    @staticmethod
    def _advance(moment: datetime, bucket: Bucket) -> datetime:
        if bucket is Bucket.HOUR:
            return moment + timedelta(hours=1)
        if bucket is Bucket.DAY:
            return moment + timedelta(days=1)
        if bucket is Bucket.WEEK:
            return moment + timedelta(days=7)
        return (moment.replace(day=28) + timedelta(days=4)).replace(day=1)
