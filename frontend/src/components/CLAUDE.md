# components

Presentational components. They receive data, they do not fetch it.

- `Layout.tsx` — sidebar, off-canvas mobile menu, and `PageHeader` for the
  sticky title/filter bar.
- `FilterBar.tsx` — period, status, chat type, chat and employee controls, bound
  to the filters context.
- `Card.tsx` — panel with optional header, hint and actions.
- `StatCard.tsx` — single KPI tile with an optional growth badge.
- `StatusBadge.tsx` — status pill, `STATUS_COLOR` and `STATUS_ORDER`: the one
  place status colors and their display order are defined.
- `StatusSplitBar.tsx` — status distribution as a single bar, plus its legend.
- `StateBlock.tsx` — empty/error block and the loading `Skeleton`.
- `ConfirmDialog.tsx` — modal confirmation for a write, with pending and error
  state.
- `Pagination.tsx` — page controls and the row-count line, shared by every list.
- `TaskDrawer.tsx` — task details and status history in a side panel.
- `charts/` — `TasksTrendChart`, `StatusDonut`, `StackedBarChart`.

`StatusSplitBar`, `StatusDonut` and `StackedBarChart` all render `STATUS_ORDER`,
so a new status appears in every one of them at once.

Charts take numeric heights, so they read breakpoints through
`useBreakpoints` instead of CSS. Tables collapse into cards under 640px using
the `data-label` attribute on each `td`; a new column needs one.
