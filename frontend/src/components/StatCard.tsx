interface StatCardProps {
  label: string;
  value: string;
  hint?: string;
  change?: number | null;
}

function changeLabel(change: number): string {
  const sign = change > 0 ? "+" : "";
  return `${sign}${Math.round(change * 100)}%`;
}

export function StatCard({ label, value, hint, change }: StatCardProps) {
  return (
    <article className="card stat">
      <span className="stat-label">{label}</span>
      <span className="stat-value numeric">{value}</span>
      <span className="stat-foot">
        {change !== null && change !== undefined && Number.isFinite(change) && (
          <span className={change >= 0 ? "trend-up" : "trend-down"}>
            {change >= 0 ? "▲" : "▼"} {changeLabel(change)}
          </span>
        )}
        {hint}
      </span>
    </article>
  );
}
