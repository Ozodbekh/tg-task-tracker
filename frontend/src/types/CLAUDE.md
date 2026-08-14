# types

API types, mirroring `docs/api/`. Nothing else defines an API shape.

- `domain.ts` — `TaskStatus`, `ChatType`, `Period`, `Bucket`, `Employee`,
  `Chat`, `Task`, `TaskEvent`, `TaskDetail`, `UnresolvedMessage`, the statistics
  responses and `Paginated`.

These follow the backend's field names, snake_case included; they are not
renamed on the way in.
