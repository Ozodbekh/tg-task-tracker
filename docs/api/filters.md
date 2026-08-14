# Filters

Shared query parameters. Every endpoint under [stats](stats.md), plus
[tasks](tasks.md) and [unresolved](unresolved.md), accepts them.
[employees](employees.md) and [chats](chats.md) listings accept none.

- `period` (required) — `day`, `week`, `month`, `quarter`, `9months`, `year`,
  `all`. The range ends now and starts `1 / 7 / 30 / 90 / 270 / 365` days back;
  `all` has no lower bound. Applied to `tasks.created_at`.
- `bucket` — `hour`, `day`, `week`, `month`. Only `/api/stats/timeseries` reads
  it. Defaults: `day → hour`, `week`/`month` → `day`, `quarter → week`,
  `9months`/`year`/`all` → `month`.
- `status` — `open`, `in_progress`, `done`, `cancelled`.
- `chat_id` — internal `chats.id`.
- `chat_type` — `private` or `group`.
- `employee_id` — internal `employees.id`.

`/api/unresolved` honors `period`, `chat_id` and `chat_type` only.

## Pagination

Every list endpoint takes the same two parameters and answers with the same
envelope:

```json
{ "items": [], "total": 0, "page": 1, "page_size": 20 }
```

- `page` — 1-based, default `1`. `400` on `0` or a negative value. A page past
  the end returns empty `items` with the real `total`, not a `404`.
- `page_size` — default `20`, maximum `100`. A larger value is clamped, not
  rejected.
- `page` and `page_size` echo what was applied, not what was asked for.
- `total` counts the rows matching the filters before paging.

Sorting is stable: every list breaks ties on `id`, so no row appears on two
pages.

Paginated: `/api/tasks`, `/api/stats/employees`, `/api/stats/chats`,
`/api/unresolved`. Unpaginated on purpose: `/api/employees` and `/api/chats`,
which fill the filter dropdowns and always return every row.
`/api/stats/timeseries` returns a bare array of buckets.

Errors: `400` with `{ "detail": "Invalid filters" }` for an unknown `period`,
`bucket`, `status`, `chat_type`, `sort`, or an out-of-range `page` /
`page_size`.

## Shared shapes

- `employee` — `{ id, telegram_id, name, created_at }`.
- `chat` — `{ id, telegram_id, type, title, created_at }`. `title` is `null` for
  private chats.
- `by_status` — `{ open, in_progress, done, cancelled }`, integers.
- `completion_rate` — float `0..1`: `done / (total - cancelled)`, `0` when the
  denominator is `0`.
- `avg_completion_seconds` — float, `done_at - created_at` averaged over done
  tasks; `null` when there are none.
- `avg_response_seconds` — float, `started_at - created_at` averaged over
  started tasks; `null` when there are none.

Timestamps are ISO 8601 with an offset. Bucket timestamps are in the server
timezone (`TIMEZONE`, `Asia/Tashkent` by default).
