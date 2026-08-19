import logging

from telethon import TelegramClient

from app.models.digest import EmployeeDigest

logger = logging.getLogger(__name__)

TEMPLATE = """Bugungi statistika:

{name}, sizda bu hafta {total} ta task yaratildi
Shundan {in_progress} ta task ish jarayonida
{done} ta task to'liq bajarildi
{paused} ta task hozircha to'xtatildi
{blocked} ta task sizga bog'liq emas holda to'xtab qolgan
{cancelled} ta task bekor qilindi, bajarish shart emas
{open} ta task hali qarab ham ko'rmadingiz

Sizda tizimni yaxshilash bo'yicha taklif bo'lsa @tg_task_tracker yozing!"""

UNTRACKED = 0


class DigestSender:
    def __init__(self, client: TelegramClient) -> None:
        self._client = client

    async def send(self, digests: list[EmployeeDigest]) -> int:
        delivered = 0
        for digest in digests:
            if await self._send_one(digest):
                delivered += 1
        return delivered

    async def _send_one(self, digest: EmployeeDigest) -> bool:
        try:
            await self._client.send_message(digest.telegram_id, self.render(digest))
        except Exception:
            logger.exception(
                "Failed to send the digest to %s (%s)",
                digest.name,
                digest.telegram_id,
            )
            return False
        logger.info("Digest sent to %s (%s)", digest.name, digest.telegram_id)
        return True

    @staticmethod
    def render(digest: EmployeeDigest) -> str:
        return TEMPLATE.format(
            name=digest.name,
            total=digest.total,
            in_progress=digest.by_status.in_progress,
            done=digest.by_status.done,
            paused=UNTRACKED,
            blocked=UNTRACKED,
            cancelled=digest.by_status.cancelled,
            open=digest.by_status.open,
        )
