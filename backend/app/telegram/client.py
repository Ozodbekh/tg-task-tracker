import asyncio
import sqlite3
from contextlib import closing
from pathlib import Path

from telethon import TelegramClient


def create_client(session_path: Path, api_id: int, api_hash: str) -> TelegramClient:
    session_path.parent.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(session_path), api_id, api_hash)


async def clone_session(source: Path, target: Path) -> None:
    await asyncio.to_thread(_snapshot, source, target)


def _snapshot(source: Path, target: Path) -> None:
    with (
        closing(sqlite3.connect(source)) as origin,
        closing(sqlite3.connect(target)) as copy,
    ):
        origin.backup(copy)
