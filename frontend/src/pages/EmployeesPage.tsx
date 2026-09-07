import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { ApiError } from "@/api/client";
import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { ConfirmDialog } from "@/components/ConfirmDialog";
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
  formatDate,
  formatDuration,
  formatNumber,
  formatPercent,
  formatRelative,
  initials,
} from "@/lib/format";
import type { EmployeeStats, StatusCounts } from "@/types/domain";

type Action = "retire" | "restore";

function unfinishedCount(counts: StatusCounts): number {
  return counts.open + counts.in_progress + counts.on_hold + counts.blocked;
}

function actionError(cause: unknown): string {
  if (cause instanceof ApiError) {
    if (cause.status === 404) return "Xodim topilmadi, ro'yxatni yangilang";
    if (cause.status >= 500) return "Server javob bermayapti, keyinroq urinib ko'ring";
  }
  return "Amalni bajarib bo'lmadi";
}

export function EmployeesPage() {
  const { filters, employees, reloadEmployees } = useFilters();
  const retiredAt = useMemo(
    () => new Map(employees.map((employee) => [employee.id, employee.left_at])),
    [employees],
  );
  const filterKey = JSON.stringify(filters);
  const { page, pageSize, setPage, setPageSize } = usePagination(filterKey);
  const stats = useResource(
    () => backend.employeeStats({ ...filters, page, page_size: pageSize }),
    [JSON.stringify({ filters, page, pageSize })],
  );

  const [target, setTarget] = useState<{
    row: EmployeeStats;
    action: Action;
    unfinished: number | null;
  } | null>(null);
  const [counting, setCounting] = useState<number | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  const rows = stats.data?.items ?? [];

  async function ask(row: EmployeeStats, action: Action) {
    setNotice(null);
    setError(null);
    if (action === "restore") {
      setTarget({ row, action, unfinished: null });
      return;
    }
    setCounting(row.employee.id);
    try {
      const all = await backend.employee(row.employee.id, { period: "all" });
      setTarget({ row, action, unfinished: unfinishedCount(all.by_status) });
    } catch {
      setTarget({ row, action, unfinished: null });
    } finally {
      setCounting(null);
    }
  }

  async function confirm() {
    if (!target) return;
    const { id } = target.row.employee;
    setPending(true);
    setError(null);
    try {
      if (target.action === "retire") {
        const result = await backend.retireEmployee(id);
        setNotice(
          `${result.employee.name} ishdan chiqarildi — ${formatNumber(result.cancelled_tasks)} ta topshiriq bekor qilindi.`,
        );
      } else {
        const employee = await backend.restoreEmployee(id);
        setNotice(`${employee.name} ishga qaytarildi.`);
      }
      setTarget(null);
      stats.reload();
      reloadEmployees();
    } catch (cause) {
      setError(actionError(cause));
    } finally {
      setPending(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Xodimlar"
        subtitle={`${periodLabel(filters.period)} kesimidagi samaradorlik`}
        filters={<FilterBar showEmployee={false} />}
      />

      <div className="content">
        <Card padded={false} actions={<StatusLegend />} title="Xodimlar kesimi">
          {notice && <p className="notice">{notice}</p>}

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
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => {
                      const leftAt = retiredAt.get(row.employee.id) ?? null;

                      return (
                        <tr key={row.employee.id} className={leftAt ? "retired" : ""}>
                          <td>
                            <Link to={`/employees/${row.employee.id}`} className="cell-main">
                              <span className="avatar">{initials(row.employee.name)}</span>
                              <span className="stack">
                                <span className="row" style={{ gap: 8 }}>
                                  <span className="cell-title">{row.employee.name}</span>
                                  {leftAt && <span className="badge badge-neutral">Ketgan</span>}
                                </span>
                                <span className="cell-sub">
                                  ID {row.employee.telegram_id}
                                  {leftAt && ` · ${formatDate(leftAt)} da ketgan`}
                                </span>
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
                                  style={{ width: `${row.completion_rate * 100}%` }}
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
                          <td data-label="Amal">
                            <button
                              type="button"
                              className="ghost-button"
                              disabled={counting === row.employee.id}
                              onClick={() => void ask(row, leftAt ? "restore" : "retire")}
                            >
                              {leftAt ? "Qaytarish" : "Ishdan chiqarish"}
                            </button>
                          </td>
                        </tr>
                      );
                    })}
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

      {target &&
        (target.action === "retire" ? (
          <ConfirmDialog
            title="Xodimni ishdan chiqarish"
            description={
              target.unfinished === null
                ? `${target.row.employee.name} ishdan chiqariladi va uning tugallanmagan barcha topshiriqlari bekor qilinadi. Buni qaytarib bo'lmaydi — xodimni qaytarsangiz ham topshiriqlar tiklanmaydi.`
                : `${target.row.employee.name}ning ${formatNumber(target.unfinished)} ta tugallanmagan topshirig'i bekor qilinadi. Buni qaytarib bo'lmaydi — xodimni qaytarsangiz ham topshiriqlar tiklanmaydi.`
            }
            confirmLabel="Ishdan chiqarish"
            danger
            pending={pending}
            error={error}
            onConfirm={confirm}
            onCancel={() => setTarget(null)}
          />
        ) : (
          <ConfirmDialog
            title="Xodimni qaytarish"
            description={`${target.row.employee.name} yana faol xodim bo'ladi. Ishdan chiqarilganda bekor qilingan topshiriqlar tiklanmaydi.`}
            confirmLabel="Qaytarish"
            pending={pending}
            error={error}
            onConfirm={confirm}
            onCancel={() => setTarget(null)}
          />
        ))}
    </>
  );
}
