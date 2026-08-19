# services

Business logic. The only caller of `db/`.

- `employees.py` — `EmployeeService.ensure` creates the employee on first sight
  and refreshes the stored name; `find`, `get` and `list_all` read.
- `chats.py` — `ChatService`, same pattern for chats.
- `tasks.py` — `TaskService`:
  - `capture` ensures the chat and the employee exist, upserts the task, and
    records an event only when the task is new or revived from `cancelled`.
  - `apply_status` accepts a status reply only from the task's own employee,
    and ignores a status equal to the current one.
  - `cancel` moves a task to `cancelled`; nothing is deleted.
  - `record_unresolved` stores a `#task` message whose assignee was not
    resolved.
  - `list_views`, `detail`, `list_unresolved` serve the panel's read screens.
- `stats.py` — `StatsService` maps the aggregate rows into models, pages the
  per-employee and per-chat rankings, and fills the timeseries gaps so the chart
  has a point per bucket.
- `auth.py` — `AuthService`: the single account, and token issuing on a
  successful login.
- `digest.py` — `DigestService.weekly` counts each employee's tasks for the
  current week. The week starts Monday at midnight in the configured timezone
  and the window runs a full seven days, so it never cuts a task off at `now`.
  Employees with no task in the week are absent from the result.
- `views.py` — row-to-model mapping and the shared `completion_rate` formula.

Notes:

- All timestamps are UTC and produced inside the service.
- Buckets are aligned in the configured timezone, not UTC, so a day starts
  locally.
