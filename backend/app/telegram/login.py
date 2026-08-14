import asyncio
from getpass import getpass

from telethon.errors import SessionPasswordNeededError

from app.core.config import settings
from app.telegram.client import create_client


class TelegramLogin:
    def __init__(self) -> None:
        self._client = create_client(
            settings.session_path, settings.api_id, settings.api_hash
        )

    async def run(self) -> None:
        await self._client.connect()
        try:
            if await self._client.is_user_authorized():
                await self._report("Session already authorized")
                return
            await self._authorize()
            await self._report("Session saved")
        finally:
            await self._client.disconnect()

    async def _authorize(self) -> None:
        phone = input("Phone number (international format): ").strip()
        await self._client.send_code_request(phone)
        code = input("Login code: ").strip()

        try:
            await self._client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            password = getpass("Two-step verification password: ")
            await self._client.sign_in(password=password)

    async def _report(self, message: str) -> None:
        user = await self._client.get_me()
        name = user.username or user.first_name or user.id
        print(f"{message}: {name}")
        print(f"Session file: {settings.session_path}")


def main() -> None:
    asyncio.run(TelegramLogin().run())


if __name__ == "__main__":
    main()
