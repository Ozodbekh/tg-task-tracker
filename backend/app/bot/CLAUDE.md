# bot

The Telegram bot. Employees ask it for their own tasks; it answers with a PDF.
Separate from `telegram/`, which is the manager's user session and only reads.

- `client.py` — builds the aiogram `Bot` from `BOT_TOKEN`, HTML parse mode.
- `handlers.py` — `BotHandlers`: `/start` explains the bot, `/my_task` (also
  `/mytask`) answers with the sender's unfinished tasks as a PDF. A sender with
  no employee row is told so rather than ignored.
- `report.py` — `TaskReport` renders the PDF with `fpdf2`. Sections run open,
  in progress, on hold, blocked; a group task carries a link back to the
  message, a private one has none.
- `webhook.py` — `BotWebhook`: the Starlette route Telegram posts to.
- `setup.py` — run through `make set-webhook`. Points Telegram at
  `BOT_WEBHOOK_URL` + the route, publishes the command menu, then prints what
  Telegram reports back, `last_error_message` included. Run it once per server
  and again whenever the URL or the secret changes; `main.py` never registers
  the webhook itself.

Notes:

- Telegram command names take only `a-z`, `0-9` and `_`, so `/my-task` is not a
  command; `/my_task` and `/mytask` both work.
- A bot cannot write to someone who has not pressed Start on it first.
- The webhook route is public to the auth middleware and guards itself with the
  `X-Telegram-Bot-Api-Secret-Token` header, compared in constant time.
- `report.py` needs a DejaVu font on the machine, from `fonts-dejavu-core`. It
  raises `MissingFontError` when there is none.
- Without `BOT_TOKEN` the bot is not built and the rest of the app runs
  unchanged.
