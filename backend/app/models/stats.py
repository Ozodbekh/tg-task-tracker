from datetime import datetime

from pydantic import BaseModel

from app.models.chat import Chat
from app.models.employee import Employee


class StatusCounts(BaseModel):
    open: int = 0
    in_progress: int = 0
    on_hold: int = 0
    blocked: int = 0
    done: int = 0
    cancelled: int = 0


class PreviousWindow(BaseModel):
    total: int
    done: int
    completion_rate: float


class Overview(BaseModel):
    total: int
    by_status: StatusCounts
    completion_rate: float
    avg_completion_seconds: float | None
    avg_response_seconds: float | None
    overdue_open: int
    unresolved: int
    active_employees: int
    active_chats: int
    previous: PreviousWindow | None


class TimeseriesPoint(BaseModel):
    bucket: datetime
    created: int
    done: int
    in_progress: int
    cancelled: int


class EmployeeStats(BaseModel):
    employee: Employee
    total: int
    by_status: StatusCounts
    completion_rate: float
    avg_completion_seconds: float | None
    avg_response_seconds: float | None
    last_activity_at: datetime | None


class ChatStats(BaseModel):
    chat: Chat
    total: int
    by_status: StatusCounts
    completion_rate: float
    unresolved: int
    participants: int
    last_task_at: datetime | None
