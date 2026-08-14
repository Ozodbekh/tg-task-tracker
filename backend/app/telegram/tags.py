import re

from app.models.task import TaskStatus

TASK_TAG = "task"
STATUS_TAGS: dict[str, TaskStatus] = {
    "inp": TaskStatus.IN_PROGRESS,
    "done": TaskStatus.DONE,
}

_TAG_PATTERN = re.compile(r"(?<!\w)#(\w+)")


class TagReader:
    @staticmethod
    def tags(text: str) -> set[str]:
        return {match.lower() for match in _TAG_PATTERN.findall(text)}

    @classmethod
    def has_task_tag(cls, text: str) -> bool:
        return TASK_TAG in cls.tags(text)

    @classmethod
    def status(cls, text: str) -> TaskStatus | None:
        for tag in cls.tags(text):
            status = STATUS_TAGS.get(tag)
            if status is not None:
                return status
        return None
