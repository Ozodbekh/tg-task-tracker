from app.models.chat import Chat, ChatType

SUPERGROUP_PREFIX = "-100"


def message_link(chat: Chat, message_id: int) -> str | None:
    if chat.type is ChatType.PRIVATE:
        return None
    identifier = str(chat.telegram_id)
    if not identifier.startswith(SUPERGROUP_PREFIX):
        return None
    return f"https://t.me/c/{identifier[len(SUPERGROUP_PREFIX) :]}/{message_id}"
