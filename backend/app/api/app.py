from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from app.api.auth import AuthRoutes
from app.api.directory import DirectoryRoutes
from app.api.filters import FilterError
from app.api.responses import invalid_filters
from app.api.security import AuthenticationMiddleware
from app.api.stats import StatsRoutes
from app.api.tasks import TaskRoutes
from app.core.config import settings
from app.services.auth import AuthService
from app.services.chats import ChatService
from app.services.employees import EmployeeService
from app.services.stats import StatsService
from app.services.tasks import TaskService


async def health(request: Request) -> Response:
    return JSONResponse({"status": "ok"})


async def on_filter_error(request: Request, exception: Exception) -> Response:
    return invalid_filters()


def create_app(
    auth: AuthService,
    tasks: TaskService,
    stats: StatsService,
    employees: EmployeeService,
    chats: ChatService,
) -> Starlette:
    routes = [
        Route("/api/health", health, methods=["GET"]),
        *AuthRoutes(auth).routes(),
        *StatsRoutes(stats).routes(),
        *TaskRoutes(tasks).routes(),
        *DirectoryRoutes(employees, chats, stats).routes(),
    ]

    middleware = [
        Middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts),
        Middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "DELETE"],
        ),
        Middleware(AuthenticationMiddleware, service=auth),
    ]

    return Starlette(
        routes=routes,
        middleware=middleware,
        exception_handlers={FilterError: on_filter_error},
    )
