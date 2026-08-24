import asyncio
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from app.core.config import settings
from app.db.database import Database
from app.db.stats import StatsRepository
from app.services.digest import DigestService
from app.telegram.client import clone_session, create_client
from app.telegram.digest import DigestSender

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    logging.getLogger("telethon").setLevel(logging.WARNING)
    logger.info("Digest run started")

    database = Database(settings.db_path)
    await database.connect()

    with TemporaryDirectory() as directory:
        session = Path(directory) / settings.session_path.name
        await clone_session(settings.session_path, session)
        client = create_client(session, settings.api_id, settings.api_hash)
        try:
            await client.connect()
            if not await client.is_user_authorized():
                raise RuntimeError("No authorized session. Run `make login` first.")

            service = DigestService(StatsRepository(database))
            digests = await service.pending()
            delivered = await DigestSender(client).send(digests)
            logger.info(
                "Digest delivered to %s of %s employees", delivered, len(digests)
            )
        finally:
            await client.disconnect()
            await database.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
