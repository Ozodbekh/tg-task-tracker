import pytest

from app.db.database import Database
from app.db.stats import StatsRepository
from app.models.chat import ChatIdentity
from app.models.employee import EmployeeIdentity
from app.models.task import StatusChange, TaskCapture, TaskStatus
from app.services.digest import DigestService
from app.services.employees import EmployeeService
from app.services.tasks import TaskService
from app.telegram.digest import DigestSender

MANAGER_ID = 1


@pytest.fixture
def digests(database: Database) -> DigestService:
    return DigestService(StatsRepository(database))


async def capture(
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
            text="#task write the report",
        )
    )


async def move(
    tasks: TaskService,
    chat: ChatIdentity,
    assignee: EmployeeIdentity,
    message_id: int,
    status: TaskStatus,
) -> None:
    await tasks.apply_status(
        StatusChange(
            chat=chat,
            task_message_id=message_id,
            status=status,
            actor_id=assignee.telegram_id,
            message_id=message_id + 100,
            text="",
        )
    )


async def backdate(database: Database, message_id: int, moment: str) -> None:
    async with database.cursor() as cursor:
        await cursor.execute(
            "UPDATE tasks SET created_at = ? WHERE message_id = ?",
            (moment, message_id),
        )


async def test_counts_every_status(
    digests: DigestService,
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    for message_id in (10, 11, 12, 13):
        await capture(tasks, group, assignee, message_id)
    await move(tasks, group, assignee, 11, TaskStatus.IN_PROGRESS)
    await move(tasks, group, assignee, 12, TaskStatus.DONE)
    await tasks.cancel(group, 13, MANAGER_ID)

    rows = await digests.pending()
    assert len(rows) == 1

    row = rows[0]
    assert row.telegram_id == assignee.telegram_id
    assert row.name == assignee.name
    assert row.total == 4
    assert row.by_status.open == 1
    assert row.by_status.in_progress == 1
    assert row.by_status.done == 1
    assert row.by_status.cancelled == 1


async def test_an_old_task_still_counts(
    digests: DigestService,
    database: Database,
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await capture(tasks, group, assignee, 10)
    await backdate(database, 10, "2024-01-15T09:00:00+00:00")

    rows = await digests.pending()
    assert [row.total for row in rows] == [1]
    assert rows[0].by_status.open == 1


async def test_employee_with_everything_done_is_skipped(
    digests: DigestService,
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    for message_id in (10, 11):
        await capture(tasks, group, assignee, message_id)
        await move(tasks, group, assignee, message_id, TaskStatus.DONE)

    assert await digests.pending() == []


async def test_one_task_left_open_still_earns_a_reminder(
    digests: DigestService,
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    for message_id in (10, 11):
        await capture(tasks, group, assignee, message_id)
    await move(tasks, group, assignee, 10, TaskStatus.DONE)

    rows = await digests.pending()
    assert [row.telegram_id for row in rows] == [assignee.telegram_id]
    assert rows[0].by_status.done == 1
    assert rows[0].by_status.open == 1


async def test_employee_without_tasks_is_skipped(
    digests: DigestService,
    tasks: TaskService,
    employees: EmployeeService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    await capture(tasks, group, assignee, 10)
    await employees.ensure(EmployeeIdentity(telegram_id=888, name="Bek"))

    rows = await digests.pending()
    assert [row.telegram_id for row in rows] == [assignee.telegram_id]


async def test_on_hold_and_blocked_reach_the_message(
    digests: DigestService,
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    for message_id in (10, 11, 12):
        await capture(tasks, group, assignee, message_id)
    await move(tasks, group, assignee, 10, TaskStatus.ON_HOLD)
    await move(tasks, group, assignee, 11, TaskStatus.BLOCKED)

    row = (await digests.pending())[0]
    assert row.by_status.on_hold == 1
    assert row.by_status.blocked == 1

    message = DigestSender.render(row)
    assert "<b>1</b> ta task hozircha to'xtatildi" in message
    assert "<b>1</b> ta task sizga bog'liq emas holda to'xtab qolgan" in message


async def test_rendered_message_carries_every_line(
    digests: DigestService,
    tasks: TaskService,
    group: ChatIdentity,
    assignee: EmployeeIdentity,
) -> None:
    for message_id in (10, 11):
        await capture(tasks, group, assignee, message_id)
    await move(tasks, group, assignee, 11, TaskStatus.DONE)

    message = DigestSender.render((await digests.pending())[0])

    assert message.startswith("<b>📌📌 Avtomatik eslatma 📌📌</b>")
    assert "Bugungi statistika:" in message
    assert f"{assignee.name}, sizda jami <b>2</b> ta task bor" in message
    assert "Shundan <b>0</b> ta task ish jarayonida" in message
    assert "<b>1</b> ta task to'liq bajarildi" in message
    assert "<b>0</b> ta task hozircha to'xtatildi" in message
    assert "<b>0</b> ta task sizga bog'liq emas holda to'xtab qolgan" in message
    assert "<b>0</b> ta task bekor qilindi, bajarish shart emas" in message
    assert "<b>1</b> ta task hali qarab ham ko'rmadingiz" in message
    assert message.endswith("@tg_task_tracker yozing!")


async def test_rendered_name_is_escaped(
    digests: DigestService,
    tasks: TaskService,
    group: ChatIdentity,
) -> None:
    await capture(
        tasks, group, EmployeeIdentity(telegram_id=42, name="A & <b>B</b>"), 10
    )

    message = DigestSender.render((await digests.pending())[0])

    assert "A &amp; &lt;b&gt;B&lt;/b&gt;" in message
