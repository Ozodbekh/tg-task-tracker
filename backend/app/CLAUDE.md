# app

The backend application package.

- `main.py` — configures logging, wires settings, database, repositories,
  services and the Telegram client together, then runs the client until it
  disconnects. It refuses to start without an authorized session.

Logging goes to stdout at `INFO`. Captures, status changes, rejected replies and
unresolved assignees are logged; every failure inside a Telegram handler is
logged with its traceback and never stops the listener.

Subpackages: `core`, `db`, `models`, `services`, `telegram`, `api`.