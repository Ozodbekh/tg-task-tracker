import pytest

from app.db.tasks import STATUS_TIMESTAMP_COLUMN
from app.models.chat import ChatIdentity
from app.models.employee import EmployeeIdentity
from app.models.task import StatusChange, TaskCapture, TaskStatus
from app.services.employees import EmployeeService
from app.services.tasks import TaskService

MANAGER_ID = 1


def test_every_status_has_a_timestamp_mapping() -> None:
    assert set(STATUS_TIMESTAMP_COLUMN) == set(TaskStatus)


def capture_of(
    chat: ChatIdentity,
    assignee: EmployeeIdentity,
    message_id: int = 10,
    text: str = "#task write the report",
) -> TaskCapture:
    return TaskCapture(
        chat=chat,
        message_id=message_id,
        author_id=MANAGER_ID,
        assignee=assignee,
        text=text,
    )


def change_of(
    chat: ChatIdentity,
    status: TaskStatus,
    actor_id: int,
    task_message_id: int = 10,
    message_id: int = 11,
    text: str = "",
) -> StatusChange:
    return StatusChange(
        chat=chat,
        task_message_id=task_message_id,
        status=status,
        actor_id=actor_id,
        message_id=message_id,
        text=text,
    )


async def test_capture_creates_task_and_employee(
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    task = await tasks.capture(capture_of(group, assignee))

    stored = await employees.find(assignee.telegram_id)
    assert stored is not None
    assert task.employee_id == stored.id
    assert task.status is TaskStatus.OPEN
    assert task.created_at is not None


async def test_capture_twice_updates_without_duplicating(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    first = await tasks.capture(capture_of(group, assignee))
    second = await tasks.capture(capture_of(group, assignee, text="#task edited"))

    assert first.id == second.id
    assert second.text == "#task edited"


async def test_capture_edit_reassigns_employee(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    first = await tasks.capture(capture_of(group, assignee))
    other = EmployeeIdentity(telegram_id=888, name="Bek")
    second = await tasks.capture(capture_of(group, other))

    assert first.id == second.id
    assert second.employee_id != first.employee_id


async def test_status_flow(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    await tasks.capture(capture_of(group, assignee))

    started = await tasks.apply_status(
        change_of(group, TaskStatus.IN_PROGRESS, assignee.telegram_id)
    )
    assert started is not None
    assert started.status is TaskStatus.IN_PROGRESS
    assert started.started_at is not None

    finished = await tasks.apply_status(
        change_of(group, TaskStatus.DONE, assignee.telegram_id, message_id=12)
    )
    assert finished is not None
    assert finished.status is TaskStatus.DONE
    assert finished.done_at is not None
    assert finished.started_at is not None


@pytest.mark.parametrize(
    "status",
    [TaskStatus.ON_HOLD, TaskStatus.BLOCKED, TaskStatus.CANCELLED],
)
async def test_employee_reply_applies_the_new_statuses(
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
    status: TaskStatus,
) -> None:
    await tasks.capture(capture_of(group, assignee))

    updated = await tasks.apply_status(change_of(group, status, assignee.telegram_id))
    assert updated is not None
    assert updated.status is status


async def test_on_hold_and_blocked_leave_the_timestamps_alone(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    await tasks.capture(capture_of(group, assignee))
    await tasks.apply_status(change_of(group, TaskStatus.ON_HOLD, assignee.telegram_id))

    blocked = await tasks.apply_status(
        change_of(group, TaskStatus.BLOCKED, assignee.telegram_id, message_id=12)
    )
    assert blocked is not None
    assert blocked.started_at is None
    assert blocked.done_at is None
    assert blocked.cancelled_at is None


async def test_a_blocked_task_can_still_be_finished(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    await tasks.capture(capture_of(group, assignee))
    await tasks.apply_status(change_of(group, TaskStatus.BLOCKED, assignee.telegram_id))

    done = await tasks.apply_status(
        change_of(group, TaskStatus.DONE, assignee.telegram_id, message_id=12)
    )
    assert done is not None
    assert done.status is TaskStatus.DONE
    assert done.done_at is not None


async def test_the_comment_sent_with_a_tag_is_stored(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    task = await tasks.capture(capture_of(group, assignee))
    comment = "#blocked ombor javob bermayapti"

    await tasks.apply_status(
        change_of(group, TaskStatus.BLOCKED, assignee.telegram_id, text=comment)
    )

    detail = await tasks.detail(task.id)
    assert detail is not None
    assert detail.status is TaskStatus.BLOCKED
    assert detail.events[-1].status is TaskStatus.BLOCKED
    assert detail.events[-1].text == comment


async def test_status_from_other_employee_is_ignored(
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await tasks.capture(capture_of(group, assignee))
    await employees.ensure(EmployeeIdentity(telegram_id=999, name="Stranger"))

    result = await tasks.apply_status(change_of(group, TaskStatus.DONE, 999))
    assert result is None


async def test_status_from_unknown_user_is_ignored(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    await tasks.capture(capture_of(group, assignee))

    result = await tasks.apply_status(change_of(group, TaskStatus.DONE, 4242))
    assert result is None


async def test_status_on_unknown_task_is_ignored(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    await tasks.capture(capture_of(group, assignee))

    result = await tasks.apply_status(
        change_of(group, TaskStatus.DONE, assignee.telegram_id, task_message_id=999)
    )
    assert result is None


async def test_cancel_and_revive(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    task = await tasks.capture(capture_of(group, assignee))

    cancelled = await tasks.cancel(group, task.message_id, MANAGER_ID)
    assert cancelled is not None
    assert cancelled.status is TaskStatus.CANCELLED
    assert cancelled.cancelled_at is not None

    revived = await tasks.capture(capture_of(group, assignee))
    assert revived.status is TaskStatus.OPEN
    assert revived.cancelled_at is None


async def test_cancel_does_not_reset_a_done_task_to_open(
    tasks: TaskService, group: ChatIdentity, assignee: EmployeeIdentity
) -> None:
    await tasks.capture(capture_of(group, assignee))
    await tasks.apply_status(change_of(group, TaskStatus.DONE, assignee.telegram_id))

    recaptured = await tasks.capture(capture_of(group, assignee))
    assert recaptured.status is TaskStatus.DONE


async def test_same_message_id_in_two_chats_are_distinct(
    tasks: TaskService,
    group: ChatIdentity,
    private: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    in_group = await tasks.capture(capture_of(group, assignee))
    in_private = await tasks.capture(capture_of(private, assignee))

    assert in_group.id != in_private.id
    assert in_group.chat_id != in_private.chat_id
