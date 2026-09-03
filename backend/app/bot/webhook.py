import logging
import secrets

from aiogram import Bot, Dispatcher
from aiogram.types import Update
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

logger = logging.getLogger(__name__)

WEBHOOK_PATH = "/api/bot/webhook"
SECRET_HEADER = "x-telegram-bot-api-secret-token"


class BotWebhook:
    def __init__(self, bot: Bot, dispatcher: Dispatcher, secret: str) -> None:
        self._bot = bot
        self._dispatcher = dispatcher
        self._secret = secret

    def routes(self) -> list[Route]:
        return [Route(WEBHOOK_PATH, self.receive, methods=["POST"])]

    async def close(self) -> None:
        await self._bot.session.close()

    async def receive(self, request: Request) -> Response:
        header = request.headers.get(SECRET_HEADER, "")
        if not secrets.compare_digest(header, self._secret):
            logger.warning("Rejected a webhook call with a wrong secret")
            return JSONResponse({"detail": "Forbidden"}, status_code=403)

        update = Update.model_validate(await request.json(), context={"bot": self._bot})
        logger.info("Update %s (%s)", update.update_id, update.event_type)
        await self._dispatcher.feed_update(self._bot, update)
        return Response(status_code=200)
