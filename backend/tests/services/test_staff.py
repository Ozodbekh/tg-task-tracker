import pytest

from app.db.database import Database
from app.db.stats import StatsRepository
from app.models.chat import ChatIdentity
from app.models.employee import EmployeeIdentity
from app.models.task import StatusChange, TaskCapture, TaskStatus
from app.services.digest import DigestService
from app.services.employees import EmployeeService
from app.services.staff import StaffService
from app.services.tasks import TaskService
from app.services.views import PANEL_NAME

MANAGER_ID = 1


@pytest.fixture
def staff(employees: EmployeeService, tasks: TaskService) -> StaffService:
    return StaffService(employees, tasks)


@pytest.fixture
def digests(database: Database) -> DigestService:
    return DigestService(StatsRepository(database))


async def give(
    tasks: TaskService,
    chat: ChatIdentity,
    assignee: EmployeeIdentity,
    message_id: int,
) -> None:
    await tasks.capture(
        TaskCapture(
            chat=chat,
            message_id=message_id,
            author_id=MANAGER_ID,
            assignee=assignee,
            text="#task do the thing",
        )
    )


async def test_retiring_cancels_every_unfinished_task(
    staff: StaffService,
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    for message_id in (10, 11, 12):
        await give(tasks, group, assignee, message_id)
    await tasks.apply_status(
        StatusChange(
            chat=group,
            task_message_id=12,
            status=TaskStatus.DONE,
            actor_id=assignee.telegram_id,
            message_id=112,
            text="#done",
        )
    )
    employee = await employees.find(assignee.telegram_id)
    assert employee is not None

    retirement = await staff.retire(employee.id)

    assert retirement is not None
    assert retirement.cancelled_tasks == 2
    assert retirement.employee.left_at is not None
    assert retirement.employee.active is False

    remaining = await tasks.for_employee(employee.id)
    assert {task.status for task in remaining} == {
        TaskStatus.CANCELLED,
        TaskStatus.DONE,
    }


async def test_the_cancellation_is_recorded_as_a_panel_event(
    staff: StaffService,
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await give(tasks, group, assignee, 10)
    employee = await employees.find(assignee.telegram_id)
    assert employee is not None
    task = (await tasks.for_employee(employee.id))[0]

    await staff.retire(employee.id)

    detail = await tasks.detail(task.id)
    assert detail is not None
    assert detail.events[-1].status is TaskStatus.CANCELLED
    assert detail.events[-1].actor_name == PANEL_NAME


async def test_a_retired_employee_gets_no_digest(
    staff: StaffService,
    digests: DigestService,
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await give(tasks, group, assignee, 10)
    employee = await employees.find(assignee.telegram_id)
    assert employee is not None
    assert len(await digests.pending()) == 1

    await staff.retire(employee.id)

    assert await digests.pending() == []


async def test_restoring_brings_the_employee_back(
    staff: StaffService,
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await give(tasks, group, assignee, 10)
    employee = await employees.find(assignee.telegram_id)
    assert employee is not None
    await staff.retire(employee.id)

    restored = await staff.restore(employee.id)

    assert restored is not None
    assert restored.left_at is None
    assert restored.active is True


async def test_a_new_task_does_not_un_retire_anyone(
    staff: StaffService,
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await give(tasks, group, assignee, 10)
    employee = await employees.find(assignee.telegram_id)
    assert employee is not None
    await staff.retire(employee.id)

    await give(tasks, group, assignee, 11)

    still_gone = await employees.find(assignee.telegram_id)
    assert still_gone is not None
    assert still_gone.active is False


async def test_an_unknown_employee_is_not_found(staff: StaffService) -> None:
    assert await staff.retire(999999) is None
    assert await staff.restore(999999) is None
