import pytest

from app.models.task import TaskStatus
from app.telegram.tags import TagReader


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("#task clean the room", True),
        ("#Task upper case", True),
        ("please #task now", True),
        ("#tasks is a different tag", False),
        ("no tag here", False),
        ("email#task is not a tag", False),
    ],
)
def test_has_task_tag(text: str, expected: bool) -> None:
    assert TagReader.has_task_tag(text) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("#inp", TaskStatus.IN_PROGRESS),
        ("#done finished it", TaskStatus.DONE),
        ("#DONE", TaskStatus.DONE),
        ("#don typo", None),
        ("nothing", None),
    ],
)
def test_status(text: str, expected: TaskStatus | None) -> None:
    assert TagReader.status(text) is expected
