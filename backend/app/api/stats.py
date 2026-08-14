from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from app.api.filters import parse_filters, parse_pagination
from app.api.responses import model, models
from app.services.stats import StatsService


class StatsRoutes:
    def __init__(self, service: StatsService) -> None:
        self._service = service

    def routes(self) -> list[Route]:
        return [
            Route("/api/stats/overview", self.overview, methods=["GET"]),
            Route("/api/stats/timeseries", self.timeseries, methods=["GET"]),
            Route("/api/stats/employees", self.employees, methods=["GET"]),
            Route("/api/stats/chats", self.chats, methods=["GET"]),
        ]

    async def overview(self, request: Request) -> Response:
        return model(await self._service.overview(parse_filters(request)))

    async def timeseries(self, request: Request) -> Response:
        return models(await self._service.timeseries(parse_filters(request)))

    async def employees(self, request: Request) -> Response:
        return model(
            await self._service.by_employee(
                parse_filters(request), parse_pagination(request)
            )
        )

    async def chats(self, request: Request) -> Response:
        return model(
            await self._service.by_chat(
                parse_filters(request), parse_pagination(request)
            )
        )
