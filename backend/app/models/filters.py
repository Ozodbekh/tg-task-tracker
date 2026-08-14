from datetime import UTC, datetime, timedelta
from enum import StrEnum

from pydantic import BaseModel

from app.models.chat import ChatType
from app.models.task import TaskStatus


class Period(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"
    NINE_MONTHS = "9months"
    YEAR = "year"
    ALL = "all"


class Bucket(StrEnum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


PERIOD_DAYS: dict[Period, int | None] = {
    Period.DAY: 1,
    Period.WEEK: 7,
    Period.MONTH: 30,
    Period.QUARTER: 90,
    Period.NINE_MONTHS: 270,
    Period.YEAR: 365,
    Period.ALL: None,
}

DEFAULT_BUCKET: dict[Period, Bucket] = {
    Period.DAY: Bucket.HOUR,
    Period.WEEK: Bucket.DAY,
    Period.MONTH: Bucket.DAY,
    Period.QUARTER: Bucket.WEEK,
    Period.NINE_MONTHS: Bucket.MONTH,
    Period.YEAR: Bucket.MONTH,
    Period.ALL: Bucket.MONTH,
}


class DateRange(BaseModel):
    start: datetime | None
    end: datetime

    @property
    def length(self) -> timedelta | None:
        return None if self.start is None else self.end - self.start

    def shifted(self) -> DateRange | None:
        length = self.length
        if self.start is None or length is None:
            return None
        return DateRange(start=self.start - length, end=self.start)


class TaskFilters(BaseModel):
    period: Period
    bucket: Bucket | None = None
    status: TaskStatus | None = None
    chat_id: int | None = None
    chat_type: ChatType | None = None
    employee_id: int | None = None

    def range(self, now: datetime | None = None) -> DateRange:
        end = now or datetime.now(UTC)
        days = PERIOD_DAYS[self.period]
        start = None if days is None else end - timedelta(days=days)
        return DateRange(start=start, end=end)

    def resolved_bucket(self) -> Bucket:
        return self.bucket or DEFAULT_BUCKET[self.period]
