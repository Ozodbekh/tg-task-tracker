from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from app.api.filters import parse_filters, parse_pagination, parse_sort
from app.api.responses import model, not_found
from app.services.tasks import TaskService


class TaskRoutes:
    def __init__(self, service: TaskService) -> None:
        self._service = service

    def routes(self) -> list[Route]:
        return [
            Route("/api/tasks", self.list, methods=["GET"]),
            Route("/api/tasks/{task_id:int}", self.detail, methods=["GET"]),
            Route("/api/unresolved", self.unresolved, methods=["GET"]),
        ]

    async def list(self, request: Request) -> Response:
        page = await self._service.list_views(
            filters=parse_filters(request),
            search=request.query_params.get("search"),
            pagination=parse_pagination(request),
            sort=parse_sort(request),
        )
        return model(page)

    async def detail(self, request: Request) -> Response:
        task = await self._service.detail(request.path_params["task_id"])
        return model(task) if task else not_found()

    async def unresolved(self, request: Request) -> Response:
        page = await self._service.list_unresolved(
            parse_filters(request), parse_pagination(request)
        )
        return model(page)
