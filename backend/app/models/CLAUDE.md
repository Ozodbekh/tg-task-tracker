# models

Pydantic models. Everything crossing a layer boundary is defined here.

- `employee.py` — `EmployeeIdentity` (what Telegram gives us) and `Employee`
  (the stored row, with `left_at` and the `active` property).
- `staff.py` — `Retirement`: the employee after retiring, and how many of
  their tasks were cancelled.
- `chat.py` — `ChatType`, `ChatIdentity`, `Chat`.
- `task.py` — the domain models (`TaskStatus`, `TaskCapture`, `Task`,
  `TaskEvent`, `StatusChange`, `UnresolvedMessage`) and the response views
  (`TaskView`, `TaskEventView`, `TaskDetail`, `UnresolvedView`).
- `filters.py` — `Period`, `Bucket`, `DateRange` and `TaskFilters`, including
  the period-to-days table and the default bucket per period.
- `stats.py` — the dashboard aggregates.
- `page.py` — `Pagination` and the generic `Page`.
- `digest.py` — `EmployeeDigest`, one employee's totals for the current week.

`*Identity` models carry Telegram ids; stored models carry internal row ids.
