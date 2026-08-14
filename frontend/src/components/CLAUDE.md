# components

Presentational components. They receive data, they do not fetch it.

- `Layout.tsx` — sidebar, off-canvas mobile menu, and `PageHeader` for the
  sticky title/filter bar.
- `FilterBar.tsx` — period, status, chat type, chat and employee controls, bound
  to the filters context.
- `Card.tsx` — panel with optional header, hint and actions.
- `StatCard.tsx` — single KPI tile with an optional growth badge.
- `StatusBadge.tsx` — status pill and `STATUS_COLOR`, the one place status
  colors are defined.
- `StatusSplitBar.tsx` — status distribution as a single bar, plus its legend.
- `StateBlock.tsx` — empty/error block and the loading `Skeleton`.
- `Pagination.tsx` — page controls and the row-count line, shared by every list.
- `TaskDrawer.tsx` — task details and status history in a side panel.
- `charts/` — `TasksTrendChart`, `StatusDonut`, `StackedBarChart`.

Charts take numeric heights, so they read breakpoints through
`useBreakpoints` instead of CSS. Tables collapse into cards under 640px using
the `data-label` attribute on each `td`; a new column needs one.
