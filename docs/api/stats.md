# Stats

Read-only dashboard aggregates. All endpoints require the session cookie and
accept the [shared filters](filters.md).

## GET /api/stats/overview

Headline numbers.

```json
{
  "total": 0,
  "by_status": {
    "open": 0, "in_progress": 0, "on_hold": 0, "blocked": 0,
    "done": 0, "cancelled": 0
  },
  "completion_rate": 0.0,
  "avg_completion_seconds": null,
  "avg_response_seconds": null,
  "overdue_open": 0,
  "unresolved": 0,
  "active_employees": 0,
  "active_chats": 0,
  "previous": { "total": 0, "done": 0, "completion_rate": 0.0 }
}
```

- `overdue_open` — tasks still `open` and older than 3 days.
- `unresolved` — `unresolved_messages` rows under the same range and chat
  filters.
- `active_employees` / `active_chats` — distinct ids among the matched tasks.
- `previous` — the same window shifted one length back; `null` when
  `period=all`.

## GET /api/stats/timeseries

One point per bucket, ascending, empty buckets included.

```json
[{ "bucket": "2026-08-14T00:00:00+05:00", "created": 0, "done": 0, "in_progress": 0, "cancelled": 0 }]
```

`created` counts tasks created in the bucket; the other three count tasks whose
current status is that value, keyed by the same `created_at` bucket. The series
carries no `on_hold` or `blocked` figure.

## GET /api/stats/employees

One row per employee with at least one task in the range, sorted by `total`
descending, then by name and id. Paginated — see
[pagination](filters.md#pagination). Asking for a small `page_size` is how the
dashboard draws its top-N chart.

```json
{ "items": [{
  "employee": {},
  "total": 0,
  "by_status": {},
  "completion_rate": 0.0,
  "avg_completion_seconds": null,
  "avg_response_seconds": null,
  "last_activity_at": null
}], "total": 0, "page": 1, "page_size": 20 }
```

`last_activity_at` — the newest `task_events.created_at` for that employee
within the range.

## GET /api/stats/chats

One row per chat with at least one task in the range, sorted by `total`
descending, then by title and id. Paginated — see
[pagination](filters.md#pagination).

```json
{ "items": [{
  "chat": {},
  "total": 0,
  "by_status": {},
  "completion_rate": 0.0,
  "unresolved": 0,
  "participants": 0,
  "last_task_at": null
}], "total": 0, "page": 1, "page_size": 20 }
```

`participants` — distinct assignees in that chat within the range.
`unresolved` — that chat's `unresolved_messages` rows within the range.
