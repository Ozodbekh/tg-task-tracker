# pages

One file per route. Pages fetch through `api/resources` and render components.

- `LoginPage.tsx` — sign-in form, shown instead of the app when there is no
  session.
- `DashboardPage.tsx` — KPI cards, trend, status donut, employee and chat
  breakdowns, latest tasks.
- `TasksPage.tsx` — filtered, searchable, paginated task list; a row opens
  `TaskDrawer`.
- `EmployeesPage.tsx` — per-employee performance table, paginated, plus the
  retire/restore control.
- `EmployeeDetailPage.tsx` — one employee: KPIs, trend, chats, and that
  employee's paginated task list.
- `ChatsPage.tsx` — chats and groups as task sources, paginated; a row sets the
  chat filter.
- `UnresolvedPage.tsx` — `#task` messages with no resolved assignee, paginated.

Retiring cancels the employee's unfinished tasks, so it asks first and reloads
the table and the employee directory afterwards. A row's counts follow the
period filter while retiring does not, so the confirmation reads the employee's
`period=all` stats for the number it names; the result line reports what the
server actually cancelled.

`left_at` arrives filled only on `GET /api/employees`, so both employee screens
take the retirement state from that directory by id rather than from the
embedded employee. The lookup goes once
`docs/handoff/frontend-to-backend/2026-09-07-1437.md` is answered.

Every page renders `PageHeader` with a `FilterBar`; a page that has no use for a
filter hides it rather than defining its own.

The dashboard and the chats chart fetch page 1 of a stats endpoint with a small
page size to get a top-N; they do not slice a full list client-side. Totals on
the chats screen come from `/api/stats/overview`, never from summing a page.
