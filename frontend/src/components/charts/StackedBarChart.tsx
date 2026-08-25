import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { STATUS_COLOR, STATUS_ORDER } from "@/components/StatusBadge";
import { useBreakpoints } from "@/hooks/useMediaQuery";
import { statusLabel } from "@/lib/filters";
import type { StatusCounts } from "@/types/domain";

export interface StackedRow extends StatusCounts {
  name: string;
}

export function StackedBarChart({ data, height = 320 }: { data: StackedRow[]; height?: number }) {
  const { mobile } = useBreakpoints();

  return (
    <ResponsiveContainer width="100%" height={mobile ? Math.max(220, data.length * 34) : height}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 12, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" horizontal={false} />
        <XAxis type="number" tickLine={false} axisLine={false} allowDecimals={false} />
        <YAxis
          type="category"
          dataKey="name"
          tickLine={false}
          axisLine={false}
          width={mobile ? 96 : 150}
          interval={0}
        />
        <Tooltip
          cursor={{ fill: "var(--surface-muted)" }}
          contentStyle={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 10,
            fontSize: 12,
          }}
        />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
        {STATUS_ORDER.map((status) => (
          <Bar
            key={status}
            dataKey={status}
            name={statusLabel(status)}
            stackId="tasks"
            fill={STATUS_COLOR[status]}
            radius={status === "cancelled" ? [0, 4, 4, 0] : undefined}
            barSize={mobile ? 12 : 16}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
