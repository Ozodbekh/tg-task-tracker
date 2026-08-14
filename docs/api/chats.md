# Chats

Chats are created automatically the first time a task is captured in them.
Group titles are refreshed on every capture.

## GET /api/chats

Every chat, sorted by title. No filters, no pagination — the filter dropdown
must see every row.

- Auth: session cookie.
- `200` — `[{ "id": 0, "telegram_id": 0, "type": "group", "title": "", "created_at": "" }]`.

`type` is `private` or `group`. `title` is `null` for private chats.

Per-chat aggregates live in [`/api/stats/chats`](stats.md).
