# API

Base path: `/api`. JSON in, JSON out. No versioning: there is one client, the
web app.

Authentication is a JWT in an httpOnly cookie. Requests must be sent with
credentials included; every endpoint except the ones marked otherwise answers
`401` without a valid cookie.

The API is read-only apart from login, logout and retiring an employee. Task
statuses change in Telegram.

## Resources

- [filters](filters.md) — shared query parameters and shared response shapes.
- [auth](auth.md) — login, logout, current session, health.
- [stats](stats.md) — overview, timeseries, per-employee and per-chat
  aggregates.
- [tasks](tasks.md) — task list, task detail with history, unresolved messages.
- [employees](employees.md) — employee list and per-employee stats.
- [chats](chats.md) — chat list.
- [bot](bot.md) — the Telegram bot webhook.
