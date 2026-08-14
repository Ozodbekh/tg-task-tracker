from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from app.models.chat import Chat, ChatIdentity
from app.models.employee import Employee, EmployeeIdentity


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskCapture(BaseModel):
    chat: ChatIdentity
    message_id: int
    author_id: int
    assignee: EmployeeIdentity
    text: str


class Task(BaseModel):
    id: int
    chat_id: int
    message_id: int
    employee_id: int
    text: str
    status: TaskStatus
    created_at: datetime
    started_at: datetime | None
    done_at: datetime | None
    cancelled_at: datetime | None


class TaskEvent(BaseModel):
    id: int
    task_id: int
    status: TaskStatus
    actor_id: int
    message_id: int
    text: str
    created_at: datetime


class StatusChange(BaseModel):
    chat: ChatIdentity
    task_message_id: int
    status: TaskStatus
    actor_id: int
    message_id: int
    text: str


class UnresolvedMessage(BaseModel):
    chat: ChatIdentity
    message_id: int
    text: str


class TaskView(BaseModel):
    id: int
    text: str
    status: TaskStatus
    message_id: int
    message_link: str | None
    employee: Employee
    chat: Chat
    created_at: datetime
    started_at: datetime | None
    done_at: datetime | None
    cancelled_at: datetime | None


class TaskEventView(BaseModel):
    id: int
    status: TaskStatus
    actor_name: str
    message_id: int
    text: str
    created_at: datetime


class TaskDetail(TaskView):
    events: list[TaskEventView]


class UnresolvedView(BaseModel):
    id: int
    chat: Chat
    message_id: int
    message_link: str | None
    text: str
    created_at: datetime
