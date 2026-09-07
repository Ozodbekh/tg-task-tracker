from datetime import UTC, datetime

from app.models.employee import Employee
from app.models.staff import Retirement
from app.services.employees import EmployeeService
from app.services.tasks import TaskService
from app.services.views import PANEL_ACTOR


class StaffService:
    def __init__(self, employees: EmployeeService, tasks: TaskService) -> None:
        self._employees = employees
        self._tasks = tasks

    async def retire(self, employee_id: int) -> Retirement | None:
        employee = await self._employees.get(employee_id)
        if employee is None:
            return None

        cancelled = await self._tasks.cancel_unfinished_for(employee_id, PANEL_ACTOR)
        updated = await self._employees.set_left_at(employee_id, datetime.now(UTC))
        if updated is None:
            return None
        return Retirement(employee=updated, cancelled_tasks=cancelled)

    async def restore(self, employee_id: int) -> Employee | None:
        employee = await self._employees.get(employee_id)
        if employee is None:
            return None
        return await self._employees.set_left_at(employee_id, None)
