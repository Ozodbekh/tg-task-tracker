from pydantic import BaseModel, ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from app.core.config import settings
from app.services.auth import AuthService


class Credentials(BaseModel):
    username: str
    password: str


class AuthRoutes:
    def __init__(self, service: AuthService) -> None:
        self._service = service

    def routes(self) -> list[Route]:
        return [
            Route("/api/auth/login", self.login, methods=["POST"]),
            Route("/api/auth/logout", self.logout, methods=["POST"]),
            Route("/api/auth/me", self.me, methods=["GET"]),
        ]

    async def login(self, request: Request) -> Response:
        try:
            credentials = Credentials(**await request.json())
        except ValidationError, ValueError:
            return JSONResponse({"detail": "Invalid payload"}, status_code=400)

        token = self._service.login(credentials.username, credentials.password)
        if token is None:
            return JSONResponse({"detail": "Invalid credentials"}, status_code=401)

        response = JSONResponse({"username": credentials.username})
        response.set_cookie(
            settings.cookie_name,
            token,
            httponly=True,
            secure=settings.cookie_secure,
            samesite="lax",
            max_age=settings.jwt_ttl_minutes * 60,
            path="/",
        )
        return response

    async def logout(self, request: Request) -> Response:
        response = Response(status_code=204)
        response.delete_cookie(settings.cookie_name, path="/")
        return response

    async def me(self, request: Request) -> Response:
        return JSONResponse({"username": request.state.username})
