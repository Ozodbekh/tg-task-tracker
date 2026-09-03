# api

HTTP layer. Parses requests, calls services, returns responses. No business
logic.

- `app.py` — `create_app` builds the Starlette app: routes, then
  `TrustedHostMiddleware`, `CORSMiddleware` and `AuthenticationMiddleware`.
  Holds `/api/health` and turns `FilterError` into `400`. Routes passed as
  `bot_routes` are mounted and made public; they authenticate themselves.
- `auth.py` — `AuthRoutes`: login, logout, current session. Login sets the JWT
  in an httpOnly cookie; the token never appears in a body.
- `security.py` — `AuthenticationMiddleware` rejects every request without a
  valid session cookie, except its `public_paths` and preflight `OPTIONS`. Puts
  the username on `request.state.username`.
- `filters.py` — parses the shared query parameters, pagination and sort into
  models. Anything invalid raises `FilterError`.
- `responses.py` — the JSON helpers every route returns through.
- `stats.py` — `StatsRoutes`: overview, timeseries, per-employee, per-chat. The
  last two are paginated; timeseries returns a bare array.
- `tasks.py` — `TaskRoutes`: task list, task detail, unresolved messages.
- `directory.py` — `DirectoryRoutes`: employee list, per-employee stats, chat
  list. An employee with no task in the range gets a zeroed row, not a `404`.
  The two listings are deliberately unpaginated; they fill filter dropdowns.

Notes:

- The API is read-only apart from login and logout.
- There is one account, from `ADMIN_USERNAME` and `ADMIN_PASSWORD_HASH`.
- `CORS_ORIGINS` must list real origins in production: browsers refuse
  credentialed requests against a wildcard.
- `COOKIE_SECURE` must stay `true` wherever the site is served over HTTPS.
