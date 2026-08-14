# Backend Rules

Python 3.14, Telethon, Starlette, aiosqlite, Pydantic. Managed with `uv` as a
workspace member.

## Scope

A backend session reads backend rules, `backend/**/CLAUDE.md`, `docs/api/`, and
the notes in `docs/handoff/frontend-to-backend/`. It does not read frontend
documentation and does not edit `frontend/`.

## Layout

```
backend/app/
  api/        HTTP layer only
  core/       settings, shared primitives
  db/         connection and SQL
  models/     Pydantic models
  services/   business logic
  telegram/   Telethon client, message parsing, event handlers
backend/tests/
```

## Layering

- `api/` parses the request, calls a service, returns a response. No business
  logic, no SQL.
- `telegram/` turns Telegram updates into service calls. It resolves Telegram
  concepts into plain data and holds no business rules.
- `services/` owns the business logic and is the only caller of `db/`.
- `db/` owns SQL and the connection. It returns data, never HTTP concepts.
- Dependencies point inward. A lower layer never imports a higher one.

## Async

- Every I/O path is `async`. No blocking call inside a coroutine.
- Offload unavoidable blocking work to a thread instead of blocking the loop.

## Database

- Parameterised SQL only. String-built queries are forbidden.
- Schema changes are explicit and versioned; no silent migrations at runtime.
- Index what is queried. No N+1 queries.
- Fetch the columns that are needed, not `SELECT *` in service paths.

## Models and configuration

- All input and output crosses a Pydantic model. Untyped dicts do not leave a
  service.
- Settings are read only through `core/config`. No `os.environ` elsewhere.
- Secrets live in `.env` and never in the repository.

## Errors

- Domain errors are explicit exception types defined in the backend, not raw
  `Exception`.
- `api/` maps domain errors to status codes. Internals never leak to the client.

## Typing and tooling

- Full type hints. `ruff` must pass clean.
- Tests mirror the package layout under `backend/tests/`.