import aiosqlite

from app.core.links import message_link
from app.models.chat import Chat
from app.models.employee import Employee
from app.models.stats import StatusCounts
from app.models.task import TaskEventView, TaskView, UnresolvedView

PANEL_ACTOR = 0
PANEL_NAME = "Panel"


def to_chat(row: aiosqlite.Row) -> Chat:
    return Chat(
        id=row["chat_id"],
        telegram_id=row["chat_telegram_id"],
        type=row["chat_type"],
        title=row["chat_title"],
        created_at=row["chat_created_at"],
    )


def to_employee(row: aiosqlite.Row) -> Employee:
    return Employee(
        id=row["employee_id"],
        telegram_id=row["employee_telegram_id"],
        name=row["employee_name"],
        created_at=row["employee_created_at"],
    )


def _actor(actor_id: int) -> str:
    return PANEL_NAME if actor_id == PANEL_ACTOR else str(actor_id)


def to_task_view(row: aiosqlite.Row) -> TaskView:
    chat = to_chat(row)
    return TaskView(
        id=row["id"],
        text=row["text"],
        status=row["status"],
        message_id=row["message_id"],
        message_link=message_link(chat, row["message_id"]),
        employee=to_employee(row),
        chat=chat,
        created_at=row["created_at"],
        started_at=row["started_at"],
        done_at=row["done_at"],
        cancelled_at=row["cancelled_at"],
    )


def to_event_view(row: aiosqlite.Row) -> TaskEventView:
    return TaskEventView(
        id=row["id"],
        status=row["status"],
        actor_name=row["actor_name"] or _actor(row["actor_id"]),
        message_id=row["message_id"],
        text=row["text"],
        created_at=row["created_at"],
    )


def to_unresolved_view(row: aiosqlite.Row) -> UnresolvedView:
    chat = to_chat(row)
    return UnresolvedView(
        id=row["id"],
        chat=chat,
        message_id=row["message_id"],
        message_link=message_link(chat, row["message_id"]),
        text=row["text"],
        created_at=row["created_at"],
    )


def to_counts(row: aiosqlite.Row) -> StatusCounts:
    return StatusCounts(
        open=row["open"],
        in_progress=row["in_progress"],
        on_hold=row["on_hold"],
        blocked=row["blocked"],
        done=row["done"],
        cancelled=row["cancelled"],
    )


def completion_rate(counts: StatusCounts, total: int) -> float:
    denominator = total - counts.cancelled
    return counts.done / denominator if denominator else 0.0
