from pathlib import Path

from telethon import TelegramClient


def create_client(session_path: Path, api_id: int, api_hash: str) -> TelegramClient:
    session_path.parent.mkdir(parents=True, exist_ok=True)
    return TelegramClient(str(session_path), api_id, api_hash)
