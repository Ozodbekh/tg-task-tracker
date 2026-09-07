# Frontend

React 19 + Vite + TypeScript. The manager's web panel: statistics, tasks,
employees and chats. Read-only except for retiring and restoring an employee.

Entry point for every frontend session. Read `../docs/rules/general.md` and
`../docs/handoff/backend-to-frontend/` first. Do not read backend
documentation. Do not edit `backend/`.

## Layout

```
src/api/         HTTP client and endpoint bindings
src/components/  presentational components
src/hooks/       React contexts and data hooks
src/lib/         filters and formatting
src/pages/       one file per route
src/types/       API types
```

## Notes

- UI text is Uzbek; code, identifiers and types are English.
- The API contract is `docs/api/`. A missing endpoint is requested through
  `docs/handoff/frontend-to-backend/`, never faked in the client.
- Auth is an httpOnly cookie, so every request goes out with
  `credentials: "include"`. The token is never read in JS.
- Filters (period, status, chat, chat type, employee) live in one context and
  apply to every screen at once.
- Every list is paginated server-side through the `{ items, total, page,
  page_size }` envelope; nothing is sliced in the client.
- `vite.config.ts` proxies `/api` to `127.0.0.1:8000` in development; `@` is an
  alias for `src`. `VITE_API_URL` must stay empty so requests are same-origin:
  the session cookie is `SameSite=lax`, so a cross-origin base URL means it is
  never sent and everything answers `401`.
- Theme is light/dark through `data-theme` on `<html>`, persisted in
  `localStorage`.
- Prettier runs at `printWidth: 100`.
