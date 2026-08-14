from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings
from app.services.auth import AuthService

PUBLIC_PATHS = frozenset({"/api/auth/login", "/api/health"})

CallNext = Callable[[Request], Awaitable[Response]]


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: object, service: AuthService) -> None:
        super().__init__(app)
        self._service = service

    async def dispatch(self, request: Request, call_next: CallNext) -> Response:
        if request.method == "OPTIONS" or request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        username = self._service.identify(request.cookies.get(settings.cookie_name))
        if username is None:
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        request.state.username = username
        return await call_next(request)
