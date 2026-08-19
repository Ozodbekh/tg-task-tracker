# app

The backend application package.

- `main.py` — configures logging, wires settings, database, repositories,
  services and the Telegram client together, then runs the client until it
  disconnects. It refuses to start without an authorized session.
- `digest.py` — one-shot entry point behind `make digest`: wires the database
  and the Telegram client, sends every employee their current-week summary,
  then exits. It refuses to run without an authorized session.

Logging goes to stdout at `INFO`. Captures, status changes, rejected replies and
unresolved assignees are logged; every failure inside a Telegram handler is
logged with its traceback and never stops the listener.

`digest.py` opens the same Telethon session file as a running `main.py`, so
while the service is up two processes hold one session.

Subpackages: `core`, `db`, `models`, `services`, `telegram`, `api`.