# Employees

Employees are created automatically the first time a task is assigned to a
Telegram user. There is no employee CRUD.

## GET /api/employees

Every employee, sorted by name. No filters, no pagination — the filter dropdown
must see every row.

- Auth: session cookie.
- `200` — `[{ "id": 0, "telegram_id": 0, "name": "", "created_at": "",
  "left_at": null }]`.

`left_at` is the moment the employee was retired, or `null` while they are
still with the company. Retired employees stay in this list so their past work
remains filterable.

## GET /api/employees/{id}/stats

One row of [`/api/stats/employees`](stats.md) for a single employee, returned
bare rather than in an envelope. Accepts the [shared filters](filters.md);
`employee_id` is taken from the path.

- `200` — the employee stats object. Counters are zero and durations `null` when
  the employee has no task in the range.
- `404` — `{ "detail": "Not found" }` when the employee does not exist.

## POST /api/employees/{id}/retire

Marks the employee as gone and cancels every task of theirs that is not
already `done` or `cancelled`.

- Auth: session cookie.
- Body: none.
- `200` — `{ "employee": {}, "cancelled_tasks": 0 }`.
- `404` — `{ "detail": "Not found" }` when the employee does not exist.

Each cancelled task gets a `cancelled` event whose `actor_name` is `Panel`.
A retired employee is dropped from the daily digest and the bot answers them
that they are no longer active. Retiring twice is harmless; it only refreshes
`left_at` and finds nothing left to cancel.

## POST /api/employees/{id}/restore

Clears `left_at`. Tasks cancelled by the retirement are not brought back.

- Auth: session cookie.
- Body: none.
- `200` — the employee object.
- `404` — `{ "detail": "Not found" }` when the employee does not exist.
