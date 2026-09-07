import logging

from aiogram import Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import BufferedInputFile, Message

from app.bot.report import TaskReport, unfinished
from app.services.employees import EmployeeService
from app.services.tasks import TaskService

logger = logging.getLogger(__name__)

COMMANDS = ("my_task", "mytask")
UPDATE_TYPES = ("message",)
FILE_NAME = "tasklarim.pdf"

START_TEXT = (
    "Salom, {name}!\n\n"
    "/my_task yuborsangiz, tasklaringiz ro'yxatini PDF qilib yuboraman.\n\n"
    "Task holatini o'zgartirish avvalgidek Telegramda bo'ladi — task xabariga "
    "reply qilib yozing:\n"
    "#inp — boshladim\n"
    "#onhold — vaqtincha to'xtatdim\n"
    "#blocked — mendan bog'liq emas\n"
    "#done — bajardim\n"
    "#cancel — bekor qilindi"
)
HINT_TEXT = "Tasklaringizni ko'rish uchun /my_task yuboring."
UNKNOWN_TEXT = "Sizni tizimda topa olmadim. Sizga hali task berilmagan bo'lishi mumkin."
LEFT_TEXT = "Siz endi tizimda faol emassiz. Savol bo'lsa rahbaringizga murojaat qiling."
FAILED_TEXT = "Hisobot tayyorlanmadi. Administratorga xabar bering."


class BotHandlers:
    def __init__(
        self,
        employees: EmployeeService,
        tasks: TaskService,
        report: TaskReport,
    ) -> None:
        self._employees = employees
        self._tasks = tasks
        self._report = report

    def dispatcher(self) -> Dispatcher:
        dispatcher = Dispatcher()
        dispatcher.message.register(self.start, CommandStart())
        dispatcher.message.register(self.my_tasks, Command(*COMMANDS))
        dispatcher.message.register(self.hint)
        return dispatcher

    async def start(self, message: Message) -> None:
        await message.answer(START_TEXT.format(name=self._name(message)))

    async def hint(self, message: Message) -> None:
        logger.info("Hint sent to %s", self._name(message))
        await message.answer(HINT_TEXT)

    @staticmethod
    def _name(message: Message) -> str:
        if message.from_user is None:
            return "do'stim"
        return message.from_user.first_name or message.from_user.full_name

    async def my_tasks(self, message: Message) -> None:
        if message.from_user is None:
            return

        employee = await self._employees.find(message.from_user.id)
        if employee is None:
            logger.info("Unknown user %s asked for tasks", message.from_user.id)
            await message.answer(UNKNOWN_TEXT)
            return

        if not employee.active:
            logger.info("Retired employee %s asked for tasks", employee.name)
            await message.answer(LEFT_TEXT)
            return

        tasks = await self._tasks.for_employee(employee.id)
        try:
            document = self._report.build(employee, tasks)
        except Exception:
            logger.exception("Failed to build the report for %s", employee.name)
            await message.answer(FAILED_TEXT)
            return

        await message.answer_document(
            BufferedInputFile(document, FILE_NAME),
            caption=(
                f"{employee.name}\n"
                f"Jami: {len(tasks)} | Bajarilmagan: {unfinished(tasks)}"
            ),
        )
        logger.info("Sent %s tasks to %s", len(tasks), employee.name)
