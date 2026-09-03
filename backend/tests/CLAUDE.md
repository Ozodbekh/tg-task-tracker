# tests

Mirrors the `app/` package layout.

- `conftest.py` — sets the environment variables `Settings` requires before any
  `app` import, then provides a `Database` on a temporary file per test and the
  services built on it.
- `services/test_tasks.py` — capture, re-capture on edit, reassignment, the
  status flow, rejected status replies, cancel and revive, chat isolation.
- `services/test_auth.py` — password hashing, token issuing, expiry, foreign
  secrets.
- `services/test_digest.py` — counts per status, old tasks, employees without a
  task, employees who finished everything, and the rendered message.
- `api/conftest.py` — a seeded database behind an `httpx.AsyncClient` driving
  the ASGI app in-process, plus a signed-in client.
- `api/test_panel.py` — auth enforcement, filters, pagination, embedded rows,
  message links, task history, `404`s and rejected filters.
- `telegram/test_tags.py` — tag matching.
- `bot/test_report.py` — the PDF builds, carries a link for a group task and
  none for a private one, and survives an empty list.
- `bot/test_webhook.py` — the secret header guards the route while the rest of
  the API stays behind the session cookie.
- `telegram/test_client.py` — session cloning while the file is held open.
- `telegram/test_digest.py` — send pacing, with `asyncio.sleep` recorded
  instead of awaited.

`asyncio_mode = "auto"`, so async tests need no marker. The Telethon layer is
not covered; it holds no business rules.
