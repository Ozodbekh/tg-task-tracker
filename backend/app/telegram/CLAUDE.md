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
- `tags.py` — `TagReader` reads hashtags: `#task` marks a task, `#inp` and
  `#done` are status tags. Matching is case-insensitive and whole-tag.
- `parser.py` — `MessageParser` resolves the chat and the assignee. In a private
  chat the assignee is the other party. In a group it tries, in order: a text
  mention carrying a `user_id`, an `@username` mention, then the replied-to
  message's sender.
- `handlers.py` — `TaskEventHandler` subscribes to `NewMessage` and
  `MessageEdited`.
- `digest.py` — `DigestSender` renders the Uzbek weekly summary and sends it to
  each employee's private chat. Messages go out one at a time with a random
  pause between them, so a large run does not read as a bot. A failed send is
  logged and the run continues.
  The message is HTML: the header and every count are bold, so the employee name
  is escaped before it goes into the template.

Notes:

- Only outgoing messages create tasks; incoming ones can only carry status tags.
- On edit, an outgoing message that lost its `#task` tag cancels the task.
- A `#task` message with no resolvable assignee is recorded as unresolved.
- The digest reports two counts the system does not track yet, paused and
  externally blocked; both are always `0`.