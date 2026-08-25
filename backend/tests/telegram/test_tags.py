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
        ("#onhold waiting on the client", TaskStatus.ON_HOLD),
        ("#ONHOLD", TaskStatus.ON_HOLD),
        ("#blocked the supplier went silent", TaskStatus.BLOCKED),
        ("#cancel not needed anymore", TaskStatus.CANCELLED),
        ("#don typo", None),
        ("#cancelled is a different tag", None),
        ("#onhold2 is a different tag", None),
        ("nothing", None),
    ],
)
def test_status(text: str, expected: TaskStatus | None) -> None:
    assert TagReader.status(text) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("#done and later #onhold", TaskStatus.DONE),
        ("#onhold and later #done", TaskStatus.ON_HOLD),
        ("#blocked then #cancel then #inp", TaskStatus.BLOCKED),
    ],
)
def test_the_first_status_tag_in_the_text_wins(
    text: str, expected: TaskStatus | None
) -> None:
    assert TagReader.status(text) is expected


def test_tags_keep_the_order_they_appear_in() -> None:
    assert TagReader.tags("#task then #done then #TASK") == ["task", "done", "task"]
