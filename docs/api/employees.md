# Employees

Employees are created automatically the first time a task is assigned to a
Telegram user. There is no employee CRUD.

## GET /api/employees

Every employee, sorted by name. No filters, no pagination — the filter dropdown
must see every row.

- Auth: session cookie.
- `200` — `[{ "id": 0, "telegram_id": 0, "name": "", "created_at": "" }]`.

## GET /api/employees/{id}/stats

One row of [`/api/stats/employees`](stats.md) for a single employee, returned
bare rather than in an envelope. Accepts the [shared filters](filters.md);
`employee_id` is taken from the path.

- `200` — the employee stats object. Counters are zero and durations `null` when
  the employee has no task in the range.
- `404` — `{ "detail": "Not found" }` when the employee does not exist.
