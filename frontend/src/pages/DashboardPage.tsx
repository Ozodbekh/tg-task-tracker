import { Link } from "react-router-dom";

import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { FilterBar } from "@/components/FilterBar";
import { PageHeader } from "@/components/Layout";
import { StatCard } from "@/components/StatCard";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { StatusBadge } from "@/components/StatusBadge";
import { StatusLegend, StatusSplitBar } from "@/components/StatusSplitBar";
import { StackedBarChart } from "@/components/charts/StackedBarChart";
import { StatusDonut } from "@/components/charts/StatusDonut";
import { TasksTrendChart } from "@/components/charts/TasksTrendChart";
import { useFilters } from "@/hooks/FiltersContext";
import { useResource } from "@/hooks/useResource";
import { bucketFor, periodLabel } from "@/lib/filters";
import {
  chatName,
  formatDuration,
  formatNumber,
  formatPercent,
  formatRelative,
} from "@/lib/format";

const TOP_ROWS = 8;

export function DashboardPage() {
  const { filters } = useFilters();
  const key = JSON.stringify(filters);

  const overview = useResource(() => backend.overview(filters), [key]);
  const timeseries = useResource(() => backend.timeseries(filters), [key]);
  const employees = useResource(
    () => backend.employeeStats({ ...filters, page: 1, page_size: TOP_ROWS }),
    [key],
  );
  const chats = useResource(
    () => backend.chatStats({ ...filters, page: 1, page_size: TOP_ROWS }),
    [key],
  );
  const recent = useResource(
    () => backend.tasks({ ...filters, page: 1, page_size: TOP_ROWS }),
    [key],
  );

  const data = overview.data;
  const growth =
    data?.previous && data.previous.total > 0
      ? (data.total - data.previous.total) / data.previous.total
      : null;

  return (
    <>
      <PageHeader
        title="Boshqaruv paneli"
        subtitle={`${periodLabel(filters.period)} kesimidagi umumiy holat`}
        filters={<FilterBar />}
      />

      <div className="content">
        {overview.error && (
          <Card>
            <StateBlock
              title="Statistikani yuklab bo'lmadi"
              description={overview.error}
              onRetry={overview.reload}
            />
          </Card>
        )}

        {overview.loading && !data ? (
          <div className="grid grid-stats">
            {[0, 1, 2, 3].map((index) => (
              <Skeleton key={index} height={104} />
            ))}
          </div>
        ) : (
          data && (
            <div className="grid grid-stats">
              <StatCard
                label="Jami topshiriq"
                value={formatNumber(data.total)}
                change={growth}
                hint="oldingi davrga nisbatan"
              />
              <StatCard
                label="Bajarilish darajasi"
                value={formatPercent(data.completion_rate)}
                hint={`${formatNumber(data.by_status.done)} ta bajarilgan`}
              />
              <StatCard
                label="O'rtacha bajarish vaqti"
                value={formatDuration(data.avg_completion_seconds)}
                hint={`javob berish: ${formatDuration(data.avg_response_seconds)}`}
              />
              <StatCard
                label="Kechikkan ochiq topshiriq"
                value={formatNumber(data.overdue_open)}
                hint={`${formatNumber(data.by_status.open)} ta ochiq`}
              />
              <StatCard
                label="Faol xodimlar"
                value={formatNumber(data.active_employees)}
                hint={`${formatNumber(data.active_chats)} ta chatda`}
              />
              <StatCard
                label="Aniqlanmagan xabarlar"
                value={formatNumber(data.unresolved)}
                hint="ijrochi topilmadi"
              />
            </div>
          )
        )}

        <div className="grid grid-2">
          <Card
            title="Topshiriqlar dinamikasi"
            hint="Berilgan va bajarilgan topshiriqlar"
            actions={<StatusLegend />}
          >
            {timeseries.loading && !timeseries.data ? (
              <Skeleton height={280} />
            ) : timeseries.data?.length ? (
              <TasksTrendChart
                data={timeseries.data}
                bucket={filters.bucket ?? bucketFor(filters.period)}
              />
            ) : (
              <StateBlock title="Bu davrda ma'lumot yo'q" />
            )}
          </Card>

          <Card title="Statuslar taqsimoti" hint="Tanlangan filtrlar bo'yicha">
            {data ? <StatusDonut counts={data.by_status} /> : <Skeleton height={220} />}
          </Card>
        </div>

        <div className="grid grid-halves">
          <Card title="Xodimlar yuklamasi" hint={`Eng ko'p topshiriq olgan ${TOP_ROWS} ta xodim`}>
            {employees.data?.items.length ? (
              <StackedBarChart
                data={employees.data.items.map((item) => ({
                  name: item.employee.name,
                  ...item.by_status,
                }))}
              />
            ) : (
              <Skeleton height={320} />
            )}
          </Card>

          <Card title="Chat va guruhlar" hint={`Eng faol ${TOP_ROWS} ta manba`}>
            {chats.data?.items.length ? (
              <StackedBarChart
                data={chats.data.items.map((item) => ({
                  name: chatName(item.chat.title, `Chat ${item.chat.telegram_id}`),
                  ...item.by_status,
                }))}
              />
            ) : (
              <Skeleton height={320} />
            )}
          </Card>
        </div>

        <Card
          title="So'nggi topshiriqlar"
          padded={false}
          actions={
            <Link to="/tasks" className="link">
              Barchasi →
            </Link>
          }
        >
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Topshiriq</th>
                  <th>Ijrochi</th>
                  <th>Chat</th>
                  <th>Status</th>
                  <th>Berilgan</th>
                </tr>
              </thead>
              <tbody>
                {recent.data?.items.map((task) => (
                  <tr key={task.id}>
                    <td>
                      <span className="cell-title">{task.text}</span>
                    </td>
                    <td data-label="Ijrochi">{task.employee.name}</td>
                    <td className="muted" data-label="Chat">
                      {chatName(task.chat.title, `Chat ${task.chat.telegram_id}`)}
                    </td>
                    <td data-label="Status">
                      <StatusBadge status={task.status} />
                    </td>
                    <td className="muted numeric" data-label="Berilgan">
                      {formatRelative(task.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!recent.loading && !recent.data?.items.length && (
              <StateBlock
                title="Topshiriq topilmadi"
                description="Filtrlarni o'zgartirib ko'ring"
              />
            )}
          </div>
        </Card>

        {data && (
          <Card title="Umumiy holat" hint="Barcha statuslar bir qatorda">
            <div className="stack" style={{ gap: 10 }}>
              <StatusSplitBar counts={data.by_status} />
              <StatusLegend />
            </div>
          </Card>
        )}
      </div>
    </>
  );
}
