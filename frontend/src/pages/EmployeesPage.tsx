import { Link } from "react-router-dom";

import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { FilterBar } from "@/components/FilterBar";
import { PageHeader } from "@/components/Layout";
import { Pagination } from "@/components/Pagination";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { StatusLegend, StatusSplitBar } from "@/components/StatusSplitBar";
import { useFilters } from "@/hooks/FiltersContext";
import { usePagination } from "@/hooks/usePagination";
import { useResource } from "@/hooks/useResource";
import { periodLabel } from "@/lib/filters";
import {
  formatDuration,
  formatNumber,
  formatPercent,
  formatRelative,
  initials,
} from "@/lib/format";

export function EmployeesPage() {
  const { filters } = useFilters();
  const filterKey = JSON.stringify(filters);
  const { page, pageSize, setPage, setPageSize } = usePagination(filterKey);
  const stats = useResource(
    () => backend.employeeStats({ ...filters, page, page_size: pageSize }),
    [JSON.stringify({ filters, page, pageSize })],
  );

  const rows = stats.data?.items ?? [];

  return (
    <>
      <PageHeader
        title="Xodimlar"
        subtitle={`${periodLabel(filters.period)} kesimidagi samaradorlik`}
        filters={<FilterBar showEmployee={false} />}
      />

      <div className="content">
        <Card padded={false} actions={<StatusLegend />} title="Xodimlar kesimi">
          {stats.error ? (
            <StateBlock title="Yuklab bo'lmadi" description={stats.error} onRetry={stats.reload} />
          ) : stats.loading && !stats.data ? (
            <div style={{ padding: 18 }}>
              <Skeleton height={320} />
            </div>
          ) : rows.length ? (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Xodim</th>
                      <th>Jami</th>
                      <th>Taqsimot</th>
                      <th>Bajarilish</th>
                      <th>O'rtacha bajarish</th>
                      <th>Javob vaqti</th>
                      <th>So'nggi faollik</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={row.employee.id}>
                        <td>
                          <Link to={`/employees/${row.employee.id}`} className="cell-main">
                            <span className="avatar">{initials(row.employee.name)}</span>
                            <span className="stack">
                              <span className="cell-title">{row.employee.name}</span>
                              <span className="cell-sub">ID {row.employee.telegram_id}</span>
                            </span>
                          </Link>
                        </td>
                        <td className="numeric" data-label="Jami">
                          {formatNumber(row.total)}
                        </td>
                        <td style={{ minWidth: 160 }} data-label="Taqsimot">
                          <StatusSplitBar counts={row.by_status} />
                        </td>
                        <td data-label="Bajarilish">
                          <div className="row">
                            <div className="bar">
                              <div
                                className="bar-fill"
                                style={{
                                  width: `${row.completion_rate * 100}%`,
                                }}
                              />
                            </div>
                            <span className="numeric">{formatPercent(row.completion_rate)}</span>
                          </div>
                        </td>
                        <td className="numeric muted" data-label="O'rtacha bajarish">
                          {formatDuration(row.avg_completion_seconds)}
                        </td>
                        <td className="numeric muted" data-label="Javob vaqti">
                          {formatDuration(row.avg_response_seconds)}
                        </td>
                        <td className="numeric muted" data-label="So'nggi faollik">
                          {formatRelative(row.last_activity_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                page={page}
                pageSize={pageSize}
                total={stats.data?.total ?? 0}
                onPage={setPage}
                onPageSize={setPageSize}
              />
            </>
          ) : (
            <StateBlock title="Ma'lumot yo'q" description="Tanlangan filtrlarda xodim topilmadi" />
          )}
        </Card>
      </div>
    </>
  );
}
