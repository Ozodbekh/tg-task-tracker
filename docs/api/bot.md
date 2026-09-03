# Bot

The Telegram bot webhook. Not part of the web panel contract; Telegram is the
only caller.

## POST /api/bot/webhook

Receives one Telegram update and feeds it to the bot.

- Auth: the `X-Telegram-Bot-Api-Secret-Token` header must equal
  `BOT_WEBHOOK_SECRET`. No session cookie; this path is exempt from it.
- Body: a Telegram `Update` object.
- `200` — empty body, whatever the update was.
- `403` — `{ "detail": "Forbidden" }` when the header is missing or wrong.

The route exists only when `BOT_TOKEN` is set. Registering it with Telegram is
a separate, explicit step: `make set-webhook`.
