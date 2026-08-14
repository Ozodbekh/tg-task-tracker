# Auth

Session is a JWT stored in an httpOnly cookie named by `COOKIE_NAME`
(`session` by default). The frontend never reads the token; it must send
requests with credentials included.

Every endpoint outside this file requires that cookie and answers `401` without
it.

## POST /api/auth/login

Signs in the single admin account.

- Auth: none.
- Body: `username` (string, required), `password` (string, required).
- `200` — `{ "username": string }`, plus the session cookie.
- `400` — `{ "detail": "Invalid payload" }` when the body is not valid JSON or a
  field is missing.
- `401` — `{ "detail": "Invalid credentials" }`.

## POST /api/auth/logout

Clears the session cookie.

- Auth: session cookie.
- Body: none.
- `204` — no content.

## GET /api/auth/me

Returns the signed-in username. Used by the frontend to restore a session on
load.

- Auth: session cookie.
- `200` — `{ "username": string }`.
- `401` — `{ "detail": "Not authenticated" }`.

## GET /api/health

Liveness probe.

- Auth: none.
- `200` — `{ "status": "ok" }`.
