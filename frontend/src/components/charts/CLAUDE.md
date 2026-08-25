# charts

Recharts wrappers. Each takes ready data and renders one chart.

- `TasksTrendChart.tsx` — created vs done over time, area chart.
- `StatusDonut.tsx` — status distribution with the total in the middle.
- `StackedBarChart.tsx` — horizontal stacked bars per employee or chat.

Colors and stacking order come from `STATUS_COLOR` and `STATUS_ORDER` in
`../StatusBadge`, never from a literal. `TasksTrendChart` is the exception: the
timeseries endpoint carries no `on_hold` or `blocked` series, so it draws only
created and done.

Heights are numeric because Recharts needs pixels, so each chart shrinks itself
through `useBreakpoints` rather than through CSS.
