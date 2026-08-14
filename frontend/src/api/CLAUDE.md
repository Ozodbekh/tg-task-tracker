# api

The HTTP layer. Nothing else in the app calls `fetch`.

- `client.ts` — `api.get` / `api.post`, `ApiError`, query building. Sends
  cookies with every request and turns a non-2xx response into `ApiError` with
  the server's `detail`.
- `resources.ts` — `backend`, one function per endpoint of `docs/api/`. Filters
  are serialized by `lib/filters`.

`204` returns `undefined`; empty query values are dropped rather than sent.

A `401` outside `/api/auth/login` and `/api/auth/me` fires the handler installed
with `setUnauthorizedHandler`, which is how an expired session sends the user
back to the login screen instead of painting an error on every card.
