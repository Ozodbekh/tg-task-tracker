import { STATUS_COLOR, STATUS_ORDER } from "@/components/StatusBadge";
import { statusLabel } from "@/lib/filters";
import type { StatusCounts } from "@/types/domain";

export function StatusSplitBar({ counts }: { counts: StatusCounts }) {
  const total = STATUS_ORDER.reduce((sum, status) => sum + counts[status], 0);
  if (!total) return <div className="split-bar" />;

  return (
    <div className="split-bar" role="img" aria-label="Statuslar taqsimoti">
      {STATUS_ORDER.map((status) => (
        <span
          key={status}
          title={`${statusLabel(status)}: ${counts[status]}`}
          style={{
            width: `${(counts[status] / total) * 100}%`,
            background: STATUS_COLOR[status],
          }}
        />
      ))}
    </div>
  );
}

export function StatusLegend() {
  return (
    <div className="legend">
      {STATUS_ORDER.map((status) => (
        <span key={status} className="legend-item">
          <span className="legend-swatch" style={{ background: STATUS_COLOR[status] }} />
          {statusLabel(status)}
        </span>
      ))}
    </div>
  );
}
