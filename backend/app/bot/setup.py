import asyncio
import logging

from aiogram.types import BotCommand

from app.bot.client import create_bot
from app.bot.webhook import WEBHOOK_PATH
from app.core.config import settings

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"

MENU = [
    BotCommand(command="my_task", description="Bajarilmagan tasklarim (PDF)"),
    BotCommand(command="start", description="Bot haqida"),
]

REQUIRED = ("bot_token", "bot_webhook_url", "bot_webhook_secret")


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    missing = [name for name in REQUIRED if not getattr(settings, name)]
    if missing:
        raise SystemExit(
            f"Missing in .env: {', '.join(name.upper() for name in missing)}"
        )

    url = f"{settings.bot_webhook_url.rstrip('/')}{WEBHOOK_PATH}"
    bot = create_bot(settings.bot_token)
    try:
        await bot.set_webhook(
            url, secret_token=settings.bot_webhook_secret, drop_pending_updates=True
        )
        await bot.set_my_commands(MENU)

        account = await bot.get_me()
        info = await bot.get_webhook_info()
        logger.info("Bot        @%s", account.username)
        logger.info("Webhook    %s", info.url)
        logger.info("Pending    %s", info.pending_update_count)
        logger.info("Last error %s", info.last_error_message or "-")
    finally:
        await bot.session.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
