import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useBreakpoints } from "@/hooks/useMediaQuery";
import { formatBucket } from "@/lib/format";
import type { Bucket, TimeseriesPoint } from "@/types/domain";

export function TasksTrendChart({ data, bucket }: { data: TimeseriesPoint[]; bucket: Bucket }) {
  const { mobile } = useBreakpoints();

  return (
    <ResponsiveContainer width="100%" height={mobile ? 220 : 280}>
      <AreaChart data={data} margin={{ top: 8, right: 8, left: mobile ? -26 : -18, bottom: 0 }}>
        <defs>
          <linearGradient id="created" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--accent)" stopOpacity={0.35} />
            <stop offset="100%" stopColor="var(--accent)" stopOpacity={0} />
          </linearGradient>
          <linearGradient id="done" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="var(--done)" stopOpacity={0.35} />
            <stop offset="100%" stopColor="var(--done)" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
        <XAxis
          dataKey="bucket"
          tickFormatter={(value: string) => formatBucket(value, bucket)}
          tickLine={false}
          axisLine={false}
          minTickGap={mobile ? 40 : 24}
        />
        <YAxis tickLine={false} axisLine={false} allowDecimals={false} width={mobile ? 32 : 44} />
        <Tooltip
          labelFormatter={(value) => formatBucket(String(value), bucket)}
          contentStyle={{
            background: "var(--surface)",
            border: "1px solid var(--border)",
            borderRadius: 10,
            fontSize: 12,
          }}
        />
        <Legend iconType="circle" wrapperStyle={{ fontSize: 12, paddingTop: 8 }} />
        <Area
          type="monotone"
          dataKey="created"
          name="Berilgan"
          stroke="var(--accent)"
          fill="url(#created)"
          strokeWidth={2}
        />
        <Area
          type="monotone"
          dataKey="done"
          name="Bajarilgan"
          stroke="var(--done)"
          fill="url(#done)"
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
