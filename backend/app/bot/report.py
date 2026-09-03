from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.models.chat import ChatType
from app.models.employee import Employee
from app.models.task import TaskStatus, TaskView

FONT_NAME = "DejaVu"
FONT_CANDIDATES = (
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
)

STATUS_TITLES: dict[TaskStatus, str] = {
    TaskStatus.OPEN: "Ochiq",
    TaskStatus.IN_PROGRESS: "Jarayonda",
    TaskStatus.ON_HOLD: "Vaqtincha to'xtatilgan",
    TaskStatus.BLOCKED: "Kutilmoqda",
    TaskStatus.DONE: "Bajarilgan",
    TaskStatus.CANCELLED: "Bekor qilingan",
}

UNFINISHED = (
    TaskStatus.OPEN,
    TaskStatus.IN_PROGRESS,
    TaskStatus.ON_HOLD,
    TaskStatus.BLOCKED,
)

FULL_WIDTH = 0
LINK_COLOR = (30, 90, 200)
TEXT_COLOR = (0, 0, 0)
LINK_LABEL = "Telegramda ochish"
EMPTY_NOTICE = "Sizda hali task yo'q."


class MissingFontError(RuntimeError):
    pass


def unfinished(tasks: list[TaskView]) -> int:
    return sum(1 for task in tasks if task.status in UNFINISHED)


def font_path() -> Path:
    for candidate in FONT_CANDIDATES:
        if candidate.exists():
            return candidate
    raise MissingFontError(
        "No DejaVu font found. Install it with `apt install fonts-dejavu-core`."
    )


class TaskReport:
    def __init__(self, timezone: str) -> None:
        self._zone = ZoneInfo(timezone)

    def build(self, employee: Employee, tasks: list[TaskView]) -> bytes:
        document = self._document()
        self._heading(document, employee, tasks)

        if not tasks:
            document.set_font(FONT_NAME, size=11)
            self._line(document, 5, EMPTY_NOTICE)
            return bytes(document.output())

        for status, title in STATUS_TITLES.items():
            group = [task for task in tasks if task.status is status]
            if group:
                self._section(document, title, group)
        return bytes(document.output())

    @staticmethod
    def _document() -> FPDF:
        regular = font_path()
        bold = regular.with_name(f"{regular.stem}-Bold{regular.suffix}")

        document = FPDF()
        document.add_font(FONT_NAME, "", str(regular))
        document.add_font(FONT_NAME, "B", str(bold if bold.exists() else regular))
        document.set_auto_page_break(auto=True, margin=15)
        document.add_page()
        return document

    @staticmethod
    def _line(
        document: FPDF, height: float, text: str, link: str | None = None
    ) -> None:
        document.multi_cell(
            FULL_WIDTH,
            height,
            text,
            link=link,
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )

    def _heading(
        self, document: FPDF, employee: Employee, tasks: list[TaskView]
    ) -> None:
        document.set_font(FONT_NAME, "B", 16)
        self._line(document, 8, employee.name)

        document.set_font(FONT_NAME, size=10)
        self._line(document, 5, f"Jami tasklar: {len(tasks)}")
        self._line(document, 5, f"Bajarilmagan: {unfinished(tasks)}")
        self._line(document, 5, f"Hisobot: {self._moment(datetime.now(self._zone))}")
        document.ln(4)

    def _section(self, document: FPDF, title: str, tasks: list[TaskView]) -> None:
        document.set_font(FONT_NAME, "B", 12)
        self._line(document, 7, f"{title} ({len(tasks)})")
        document.ln(1)

        for number, task in enumerate(tasks, start=1):
            self._task(document, number, task)
        document.ln(3)

    def _task(self, document: FPDF, number: int, task: TaskView) -> None:
        document.set_font(FONT_NAME, size=10)
        self._line(document, 5, f"{number}. {self._body(task)}")

        document.set_font(FONT_NAME, size=8)
        self._line(
            document,
            4,
            f"    Berilgan: {self._moment(task.created_at)} | {self._where(task)}",
        )

        if task.message_link:
            document.set_text_color(*LINK_COLOR)
            self._line(document, 4, f"    {LINK_LABEL}", task.message_link)
            document.set_text_color(*TEXT_COLOR)
        document.ln(2)

    @staticmethod
    def _body(task: TaskView) -> str:
        return " ".join(task.text.split())

    @staticmethod
    def _where(task: TaskView) -> str:
        if task.chat.type is ChatType.PRIVATE:
            return "Shaxsiy chat"
        return f"Guruh: {task.chat.title or task.chat.telegram_id}"

    def _moment(self, value: datetime) -> str:
        return value.astimezone(self._zone).strftime("%Y-%m-%d %H:%M")
