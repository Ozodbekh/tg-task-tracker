# charts

Recharts wrappers. Each takes ready data and renders one chart.

- `TasksTrendChart.tsx` — created vs done over time, area chart.
- `StatusDonut.tsx` — status distribution with the total in the middle.
- `StackedBarChart.tsx` — horizontal stacked bars per employee or chat.

Colors come from `STATUS_COLOR` in `../StatusBadge`, never from a literal.
Heights are numeric because Recharts needs pixels, so each chart shrinks itself
through `useBreakpoints` rather than through CSS.
