from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from app.api.filters import parse_filters
from app.api.responses import model, models, not_found
from app.models.employee import Employee
from app.models.stats import EmployeeStats, StatusCounts
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.stats import StatsService


def empty_stats(employee: Employee) -> EmployeeStats:
    return EmployeeStats(
        employee=employee,
        total=0,
        by_status=StatusCounts(),
        completion_rate=0.0,
        avg_completion_seconds=None,
        avg_response_seconds=None,
        last_activity_at=None,
    )


class DirectoryRoutes:
    def __init__(
        self,
        employees: EmployeeService,
        chats: ChatService,
        stats: StatsService,
    ) -> None:
        self._employees = employees
        self._chats = chats
        self._stats = stats

    def routes(self) -> list[Route]:
        return [
            Route("/api/employees", self.employees, methods=["GET"]),
            Route(
                "/api/employees/{employee_id:int}/stats",
                self.employee_stats,
                methods=["GET"],
            ),
            Route("/api/chats", self.chats, methods=["GET"]),
        ]

    async def employees(self, request: Request) -> Response:
        return models(await self._employees.list_all())

    async def employee_stats(self, request: Request) -> Response:
        employee_id = request.path_params["employee_id"]
        employee = await self._employees.get(employee_id)
        if employee is None:
            return not_found()

        stats = await self._stats.for_employee(parse_filters(request), employee_id)
        return model(stats or empty_stats(employee))

    async def chats(self, request: Request) -> Response:
        return models(await self._chats.list_all())
