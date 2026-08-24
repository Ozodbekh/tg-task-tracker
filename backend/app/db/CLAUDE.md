# db

SQL and the SQLite connection. The only layer that writes SQL.

- `database.py` — `Database` owns a single aiosqlite connection, applies
  `schema.sql` on connect, and hands out cursors that commit on success and roll
  back on failure.
- `schema.sql` — full schema, applied idempotently on every start.
- `filters.py` — turns `TaskFilters` and a `DateRange` into a parameterised
  `WHERE` clause, and names the two `FROM` sources every query joins through.
- `employees.py` — `EmployeeRepository`: upsert by `telegram_id`, get, list.
- `chats.py` — `ChatRepository`: upsert by `telegram_id`, get, list.
- `tasks.py` — `TaskRepository`: task writes, events, unresolved messages, and
  the read queries behind the panel lists.
- `stats.py` — `StatsRepository`: the aggregate queries behind the dashboard,
  plus the per-employee digest counts, which take no date window.
- `seed.py` — `Seeder`, run through `make seed`. Wipes every table and writes a
  deterministic fake dataset spanning the last 400 days.

Notes:

- `tasks.chat_id` and `tasks.employee_id` are internal row ids, not Telegram
  ids. `task_events.actor_id` is a raw Telegram id.
- A task is unique by `(chat_id, message_id)`. Re-capturing an existing message
  updates it and revives it from `cancelled` back to `open`; it never resets a
  live status.
- Status timestamps are written through `STATUS_TIMESTAMP_COLUMN`.
- Timestamps are stored as ISO 8601 text and compared with `datetime()` so the
  stored offset is honored.
- `make seed` is destructive; never run it against a real database.
