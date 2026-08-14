# tests

Mirrors the `app/` package layout.

- `conftest.py` — sets the environment variables `Settings` requires before any
  `app` import, then provides a `Database` on a temporary file per test and the
  services built on it.
- `services/test_tasks.py` — capture, re-capture on edit, reassignment, the
  status flow, rejected status replies, cancel and revive, chat isolation.
- `services/test_auth.py` — password hashing, token issuing, expiry, foreign
  secrets.
- `api/conftest.py` — a seeded database behind an `httpx.AsyncClient` driving
  the ASGI app in-process, plus a signed-in client.
- `api/test_panel.py` — auth enforcement, filters, pagination, embedded rows,
  message links, task history, `404`s and rejected filters.
- `telegram/test_tags.py` — tag matching.

`asyncio_mode = "auto"`, so async tests need no marker. The Telethon layer is
not covered; it holds no business rules.
