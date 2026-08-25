import { Link, useParams } from "react-router-dom";

import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { FilterBar } from "@/components/FilterBar";
import { PageHeader } from "@/components/Layout";
import { Pagination } from "@/components/Pagination";
import { StatCard } from "@/components/StatCard";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { StatusBadge } from "@/components/StatusBadge";
import { StackedBarChart } from "@/components/charts/StackedBarChart";
import { StatusDonut } from "@/components/charts/StatusDonut";
import { TasksTrendChart } from "@/components/charts/TasksTrendChart";
import { useFilters } from "@/hooks/FiltersContext";
import { usePagination } from "@/hooks/usePagination";
import { useResource } from "@/hooks/useResource";
import { bucketFor, periodLabel } from "@/lib/filters";
import {
  chatName,
  formatDateTime,
  formatDuration,
  formatNumber,
  formatPercent,
  initials,
} from "@/lib/format";

export function EmployeeDetailPage() {
  const { id } = useParams();
  const employeeId = Number(id);
  const { filters } = useFilters();
  const scoped = { ...filters, employee_id: employeeId };
  const key = JSON.stringify(scoped);

  const stats = useResource(() => backend.employee(employeeId, scoped), [key]);
  const timeseries = useResource(() => backend.timeseries(scoped), [key]);
  const chats = useResource(() => backend.chatStats({ ...scoped, page: 1, page_size: 8 }), [key]);

  const { page, pageSize, setPage, setPageSize } = usePagination(key);
  const tasks = useResource(
    () => backend.tasks({ ...scoped, page, page_size: pageSize }),
    [JSON.stringify({ scoped, page, pageSize })],
  );

  const data = stats.data;

  return (
    <>
      <PageHeader
        title={data?.employee.name ?? "Xodim"}
        subtitle={`${periodLabel(filters.period)} kesimidagi shaxsiy statistika`}
        filters={<FilterBar showEmployee={false} />}
        actions={
          <Link to="/employees" className="ghost-button">
            ← Xodimlar
          </Link>
        }
      />

      <div className="content">
        {stats.error && (
          <Card>
            <StateBlock title="Yuklab bo'lmadi" description={stats.error} onRetry={stats.reload} />
          </Card>
        )}

        {data && (
          <Card>
            <div className="row">
              <span className="avatar avatar-lg">{initials(data.employee.name)}</span>
              <div className="stack">
                <span style={{ fontSize: 17, fontWeight: 650 }}>{data.employee.name}</span>
                <span className="cell-sub">
                  Telegram ID {data.employee.telegram_id} · ro'yxatda{" "}
                  {formatDateTime(data.employee.created_at)}
                </span>
              </div>
            </div>
          </Card>
        )}

        {data ? (
          <div className="grid grid-stats">
            <StatCard label="Jami topshiriq" value={formatNumber(data.total)} />
            <StatCard label="Bajarilgan" value={formatNumber(data.by_status.done)} />
            <StatCard label="Bajarilish darajasi" value={formatPercent(data.completion_rate)} />
            <StatCard
              label="O'rtacha bajarish"
              value={formatDuration(data.avg_completion_seconds)}
              hint={`javob: ${formatDuration(data.avg_response_seconds)}`}
            />
          </div>
        ) : (
          <Skeleton height={104} />
        )}

        <div className="grid grid-2">
          <Card title="Faollik dinamikasi">
            {timeseries.data?.length ? (
              <TasksTrendChart
                data={timeseries.data}
                bucket={filters.bucket ?? bucketFor(filters.period)}
              />
            ) : (
              <Skeleton height={280} />
            )}
          </Card>
          <Card title="Statuslar">
            {data ? <StatusDonut counts={data.by_status} /> : <Skeleton height={220} />}
          </Card>
        </div>

        <Card title="Chatlar bo'yicha" hint="Xodim qaysi chatdan topshiriq oladi">
          {chats.data?.items.length ? (
            <StackedBarChart
              data={chats.data.items.map((item) => ({
                name: chatName(item.chat.title, `Chat ${item.chat.telegram_id}`),
                ...item.by_status,
              }))}
            />
          ) : (
            <StateBlock title="Ma'lumot yo'q" />
          )}
        </Card>

        <Card title="Topshiriqlar" padded={false}>
          {tasks.error ? (
            <StateBlock title="Yuklab bo'lmadi" description={tasks.error} onRetry={tasks.reload} />
          ) : tasks.loading && !tasks.data ? (
            <div style={{ padding: 18 }}>
              <Skeleton height={280} />
            </div>
          ) : tasks.data?.items.length ? (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Topshiriq</th>
                      <th>Chat</th>
                      <th>Status</th>
                      <th>Berilgan</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.data.items.map((task) => (
                      <tr key={task.id}>
                        <td>
                          <span className="cell-title">{task.text}</span>
                        </td>
                        <td className="muted" data-label="Chat">
                          {chatName(task.chat.title, `Chat ${task.chat.telegram_id}`)}
                        </td>
                        <td data-label="Status">
                          <StatusBadge status={task.status} />
                        </td>
                        <td className="muted numeric" data-label="Berilgan">
                          {formatDateTime(task.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                page={page}
                pageSize={pageSize}
                total={tasks.data.total}
                onPage={setPage}
                onPageSize={setPageSize}
              />
            </>
          ) : (
            <StateBlock title="Topshiriq topilmadi" description="Filtrlarni o'zgartirib ko'ring" />
          )}
        </Card>
      </div>
    </>
  );
}
