from datetime import UTC, datetime

import pytest

from app.bot.report import EMPTY_NOTICE, TaskReport
from app.models.chat import Chat, ChatType
from app.models.employee import Employee
from app.models.task import TaskStatus, TaskView

MOMENT = datetime(2026, 9, 3, 8, 30, tzinfo=UTC)


@pytest.fixture
def employee() -> Employee:
    return Employee(id=1, telegram_id=777, name="Ali Valiyev", created_at=MOMENT)


@pytest.fixture
def report() -> TaskReport:
    return TaskReport("Asia/Tashkent")


def chat_of(kind: ChatType) -> Chat:
    return Chat(
        id=1 if kind is ChatType.GROUP else 2,
        telegram_id=-1001 if kind is ChatType.GROUP else 555,
        type=kind,
        title="Sales team" if kind is ChatType.GROUP else None,
        created_at=MOMENT,
    )


def view_of(
    identifier: int,
    status: TaskStatus,
    kind: ChatType,
    employee: Employee,
    link: str | None,
) -> TaskView:
    return TaskView(
        id=identifier,
        text=f"#task number {identifier}",
        status=status,
        message_id=identifier,
        message_link=link,
        employee=employee,
        chat=chat_of(kind),
        created_at=MOMENT,
        started_at=None,
        done_at=None,
        cancelled_at=None,
    )


def test_report_is_a_pdf(report: TaskReport, employee: Employee) -> None:
    tasks = [
        view_of(1, TaskStatus.OPEN, ChatType.GROUP, employee, "https://t.me/c/1/1"),
        view_of(2, TaskStatus.IN_PROGRESS, ChatType.PRIVATE, employee, None),
    ]

    document = report.build(employee, tasks)

    assert document.startswith(b"%PDF")
    assert document.rstrip().endswith(b"%%EOF")


def test_a_group_link_reaches_the_document(
    report: TaskReport, employee: Employee
) -> None:
    linked = report.build(
        employee,
        [view_of(1, TaskStatus.OPEN, ChatType.GROUP, employee, "https://t.me/c/1/9")],
    )
    plain = report.build(
        employee, [view_of(1, TaskStatus.OPEN, ChatType.PRIVATE, employee, None)]
    )

    assert b"/URI" in linked
    assert b"/URI" not in plain


def test_an_empty_report_still_builds(report: TaskReport, employee: Employee) -> None:
    document = report.build(employee, [])

    assert document.startswith(b"%PDF")
    assert len(document) > 0
    assert EMPTY_NOTICE


@pytest.mark.parametrize(
    "status",
    [
        TaskStatus.OPEN,
        TaskStatus.IN_PROGRESS,
        TaskStatus.ON_HOLD,
        TaskStatus.BLOCKED,
    ],
)
def test_every_unfinished_status_renders(
    report: TaskReport, employee: Employee, status: TaskStatus
) -> None:
    document = report.build(
        employee, [view_of(1, status, ChatType.GROUP, employee, None)]
    )

    assert document.startswith(b"%PDF")
