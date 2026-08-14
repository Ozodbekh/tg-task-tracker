from datetime import UTC, datetime

from app.db.employees import EmployeeRepository
from app.models.employee import Employee, EmployeeIdentity


class EmployeeService:
    def __init__(self, repository: EmployeeRepository) -> None:
        self._repository = repository

    async def ensure(self, identity: EmployeeIdentity) -> Employee:
        return await self._repository.upsert(identity, datetime.now(UTC))

    async def find(self, telegram_id: int) -> Employee | None:
        return await self._repository.get_by_telegram_id(telegram_id)

    async def get(self, employee_id: int) -> Employee | None:
        return await self._repository.get(employee_id)

    async def list_all(self) -> list[Employee]:
        return await self._repository.list_all()
