# types

API types, mirroring `docs/api/`. Nothing else defines an API shape.

- `domain.ts` — `TaskStatus`, `ChatType`, `Period`, `Bucket`, `Employee`,
  `Chat`, `Task`, `TaskEvent`, `TaskDetail`, `UnresolvedMessage`,
  `RetiredEmployee`, the statistics responses and `Paginated`.

These follow the backend's field names, snake_case included; they are not
renamed on the way in.

An employee with a `left_at` has been retired; they stay in every list so their
past tasks remain filterable.

`on_hold` and `blocked` stamp no column on a task: `started_at`, `done_at` and
`cancelled_at` stay `null` for them, and the moment of the change is only in
`TaskDetail.events`.
