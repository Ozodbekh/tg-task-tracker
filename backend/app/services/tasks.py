from datetime import UTC, datetime

from app.db.tasks import TaskRepository
from app.models.chat import ChatIdentity
from app.models.filters import TaskFilters
from app.models.page import Page, Pagination
from app.models.task import (
    StatusChange,
    Task,
    TaskCapture,
    TaskDetail,
    TaskStatus,
    TaskView,
    UnresolvedMessage,
    UnresolvedView,
)
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.views import to_event_view, to_task_view, to_unresolved_view


class TaskService:
    def __init__(
        self,
        repository: TaskRepository,
        chats: ChatService,
        employees: EmployeeService,
    ) -> None:
        self._repository = repository
        self._chats = chats
        self._employees = employees

    async def capture(
        self, capture: TaskCapture, moment: datetime | None = None
    ) -> Task:
        now = moment or self._now()
        chat = await self._chats.ensure(capture.chat)
        employee = await self._employees.ensure(capture.assignee)
        previous = await self._repository.get(chat.id, capture.message_id)
        task = await self._repository.upsert(
            chat_id=chat.id,
            message_id=capture.message_id,
            employee_id=employee.id,
            text=capture.text,
            now=now,
        )

        if previous is None or previous.status is TaskStatus.CANCELLED:
            await self._repository.add_event(
                task_id=task.id,
                status=task.status,
                actor_id=capture.author_id,
                message_id=capture.message_id,
                text=capture.text,
                now=now,
            )
        return task

    async def apply_status(
        self, change: StatusChange, moment: datetime | None = None
    ) -> Task | None:
        task = await self._find_task(change.chat, change.task_message_id)
        if task is None:
            return None

        actor = await self._employees.find(change.actor_id)
        if actor is None or actor.id != task.employee_id:
            return None
        if task.status is change.status:
            return task

        now = moment or self._now()
        updated = await self._repository.set_status(task.id, change.status, now)
        if updated is None:
            return None

        await self._repository.add_event(
            task_id=task.id,
            status=change.status,
            actor_id=change.actor_id,
            message_id=change.message_id,
            text=change.text,
            now=now,
        )
        return updated

    async def cancel(
        self, chat: ChatIdentity, message_id: int, actor_id: int
    ) -> Task | None:
        task = await self._find_task(chat, message_id)
        if task is None or task.status is TaskStatus.CANCELLED:
            return None

        now = self._now()
        updated = await self._repository.set_status(task.id, TaskStatus.CANCELLED, now)
        if updated is None:
            return None

        await self._repository.add_event(
            task_id=task.id,
            status=TaskStatus.CANCELLED,
            actor_id=actor_id,
            message_id=message_id,
            text="",
            now=now,
        )
        return updated

    async def list_views(
        self,
        filters: TaskFilters,
        search: str | None,
        pagination: Pagination,
        sort: str,
    ) -> Page[TaskView]:
        rows, total = await self._repository.list_views(
            filters, filters.range(), search, pagination, sort
        )
        return Page(
            items=[to_task_view(row) for row in rows],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def for_employee(self, employee_id: int) -> list[TaskView]:
        rows = await self._repository.for_employee(employee_id)
        return [to_task_view(row) for row in rows]

    async def detail(self, task_id: int) -> TaskDetail | None:
        row = await self._repository.view(task_id)
        if row is None:
            return None
        events = await self._repository.events(task_id)
        return TaskDetail(
            **to_task_view(row).model_dump(),
            events=[to_event_view(event) for event in events],
        )

    async def list_unresolved(
        self, filters: TaskFilters, pagination: Pagination
    ) -> Page[UnresolvedView]:
        rows, total = await self._repository.list_unresolved(
            filters, filters.range(), pagination
        )
        return Page(
            items=[to_unresolved_view(row) for row in rows],
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def record_unresolved(
        self, message: UnresolvedMessage, moment: datetime | None = None
    ) -> None:
        chat = await self._chats.ensure(message.chat)
        await self._repository.save_unresolved(
            chat.id, message.message_id, message.text, moment or self._now()
        )

    async def find(self, chat: ChatIdentity, message_id: int) -> Task | None:
        return await self._find_task(chat, message_id)

    async def _find_task(self, identity: ChatIdentity, message_id: int) -> Task | None:
        chat = await self._chats.find(identity.telegram_id)
        if chat is None:
            return None
        return await self._repository.get(chat.id, message_id)

    @staticmethod
    def _now() -> datetime:
        return datetime.now(UTC)
