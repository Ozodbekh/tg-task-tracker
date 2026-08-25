import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { STATUS_COLOR, STATUS_ORDER } from "@/components/StatusBadge";
import { useBreakpoints } from "@/hooks/useMediaQuery";
import { statusLabel } from "@/lib/filters";
import { formatNumber } from "@/lib/format";
import type { StatusCounts } from "@/types/domain";

export function StatusDonut({ counts }: { counts: StatusCounts }) {
  const { mobile } = useBreakpoints();
  const data = STATUS_ORDER.map((status) => ({
    name: statusLabel(status),
    value: counts[status],
    color: STATUS_COLOR[status],
  })).filter((item) => item.value > 0);

  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <div style={{ position: "relative" }}>
      <ResponsiveContainer width="100%" height={mobile ? 190 : 220}>
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            nameKey="name"
            innerRadius={mobile ? 54 : 64}
            outerRadius={mobile ? 78 : 92}
            paddingAngle={2}
            stroke="none"
          >
            {data.map((item) => (
              <Cell key={item.name} fill={item.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: 10,
              fontSize: 12,
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "grid",
          placeContent: "center",
          textAlign: "center",
          pointerEvents: "none",
        }}
      >
        <span className="stat-value numeric">{formatNumber(total)}</span>
        <span className="cell-sub">jami topshiriq</span>
      </div>
    </div>
  );
}
