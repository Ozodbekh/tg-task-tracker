# telegram

Telethon layer. Turns Telegram updates into service calls and holds no business
rules.

- `client.py` — builds the `TelegramClient` from the session path and API
  credentials. A user session on the manager's account, not a bot.
  `clone_session` snapshots a session file through the SQLite backup API, so a
  second process can use the account without touching the original.
- `login.py` — `TelegramLogin`, run through `make login`. Asks for the phone
  number and the login code, and for the two-step verification password when the
  account has it enabled. Writes the session file and exits. Run it once per
  server before starting the app; `main.py` refuses to start without an
  authorized session instead of prompting.
- `tags.py` — `TagReader` reads hashtags: `#task` marks a task; `#inp`,
  `#onhold`, `#blocked`, `#done` and `#cancel` are status tags. Matching is
  case-insensitive and whole-tag. `tags` keeps the order they appear in, so a
  message with two status tags resolves to the first one, not an arbitrary one.
- `parser.py` — `MessageParser` resolves the chat and the assignee. In a private
  chat the assignee is the other party. In a group `assignees` returns every
  mentioned user in the order they appear, deduplicated, falling back to the
  replied-to message's sender when nothing is mentioned; `assignee` takes the
  first of them.
- `handlers.py` — `TaskEventHandler` subscribes to `NewMessage` and
  `MessageEdited`.
- `digest.py` — `DigestSender` renders the Uzbek task summary and sends it to
  each employee's private chat. Messages go out one at a time with a random
  pause between them, so a large run does not read as a bot. A failed send is
  logged and the run continues.
  The message is HTML: the header and every count are bold, so the employee name
  is escaped before it goes into the template.

- `backfill.py` — `HistoryBackfill` walks a chat oldest to newest and feeds it
  through the same rules as the live handler. It skips a message whose task is
  already stored rather than re-capturing it, and only applies a status reply to
  a task it captured in the same run, so replaying history can never move a
  live task backwards. It sleeps every `SLEEP_EVERY` messages.

Notes:

- Only outgoing messages create tasks; incoming ones can only carry status tags.
- On edit, an outgoing message that lost its `#task` tag cancels the task.
- A `#task` message with no resolvable assignee is recorded as unresolved.
- A message mentioning several people still makes one task, for the first of
  them; `tasks` is unique on `(chat_id, message_id)`. The backfill counts and
  logs these messages so they can be found.
- `#cancel` from the assignee and a `#task` tag removed by an edit both land on
  `cancelled`; the edit path stores no comment, the reply path stores the text
  sent with the tag.