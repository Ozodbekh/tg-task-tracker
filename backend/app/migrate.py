import asyncio
import logging

from app.core.config import settings
from app.db.database import Database
from app.db.migrate import Migrator

logger = logging.getLogger(__name__)

LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"


async def run() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    database = Database(settings.db_path)
    await database.connect()
    try:
        applied = await Migrator(database).apply()
    finally:
        await database.close()

    if not applied:
        logger.info("Nothing to apply, the schema is current")
        return
    for version in applied:
        logger.info("Applied %s", version)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
