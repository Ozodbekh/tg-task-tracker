# app

The backend application package.

- `main.py` — configures logging, wires settings, database, repositories,
  services and the Telegram client together, then runs the client until it
  disconnects. It refuses to start without an authorized session.
- `digest.py` — one-shot entry point behind `make digest`: wires the database
  and the Telegram client, sends every employee with unfinished work their
  task summary, then exits. It refuses to run without an authorized session.
- `backfill.py` — one-shot entry point, `python -m app.backfill <chat_id>
  [--apply]`. Replays a chat's whole history through the same parser and tags
  the listener uses. Without `--apply` it writes nothing and only reports.

Logging goes to stdout at `INFO`. Captures, status changes, rejected replies and
unresolved assignees are logged; every failure inside a Telegram handler is
logged with its traceback and never stops the listener.

`digest.py` runs against a throwaway copy of the Telethon session. Sharing the
file with a running `main.py` locks it, and writing to it would overwrite the
listener's update state and make it miss messages.

Subpackages: `core`, `db`, `models`, `services`, `telegram`, `api`.