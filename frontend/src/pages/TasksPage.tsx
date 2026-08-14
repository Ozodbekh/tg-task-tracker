import { useState } from "react";

import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { FilterBar } from "@/components/FilterBar";
import { PageHeader } from "@/components/Layout";
import { Pagination } from "@/components/Pagination";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { StatusBadge } from "@/components/StatusBadge";
import { TaskDrawer } from "@/components/TaskDrawer";
import { useFilters } from "@/hooks/FiltersContext";
import { useDebounced, usePagination } from "@/hooks/usePagination";
import { useResource } from "@/hooks/useResource";
import { chatName, formatDateTime } from "@/lib/format";

export function TasksPage() {
  const { filters } = useFilters();
  const [search, setSearch] = useState("");
  const [openTask, setOpenTask] = useState<number | null>(null);
  const debouncedSearch = useDebounced(search);
  const { page, pageSize, setPage, setPageSize } = usePagination(
    JSON.stringify({ filters, debouncedSearch }),
  );

  const key = JSON.stringify({ filters, debouncedSearch, page, pageSize });
  const tasks = useResource(
    () =>
      backend.tasks({
        ...filters,
        search: debouncedSearch,
        page,
        page_size: pageSize,
      }),
    [key],
  );

  const total = tasks.data?.total ?? 0;

  return (
    <>
      <PageHeader
        title="Topshiriqlar"
        subtitle="Telegramdan yig'ilgan barcha topshiriqlar"
        filters={<FilterBar />}
        actions={
          <input
            className="input"
            placeholder="Matn bo'yicha qidirish…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        }
      />

      <div className="content">
        <Card padded={false}>
          {tasks.error ? (
            <StateBlock
              title="Ro'yxatni yuklab bo'lmadi"
              description={tasks.error}
              onRetry={tasks.reload}
            />
          ) : tasks.loading && !tasks.data ? (
            <div style={{ padding: 18 }}>
              <Skeleton height={360} />
            </div>
          ) : tasks.data?.items.length ? (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Topshiriq</th>
                      <th>Ijrochi</th>
                      <th>Chat</th>
                      <th>Status</th>
                      <th>Berilgan</th>
                      <th>Yakunlangan</th>
                    </tr>
                  </thead>
                  <tbody>
                    {tasks.data.items.map((task) => (
                      <tr key={task.id} className="clickable" onClick={() => setOpenTask(task.id)}>
                        <td>
                          <span className="cell-title">{task.text}</span>
                        </td>
                        <td data-label="Ijrochi">{task.employee.name}</td>
                        <td className="muted" data-label="Chat">
                          {chatName(task.chat.title, `Chat ${task.chat.telegram_id}`)}
                          <span className="cell-sub">
                            {task.chat.type === "group" ? " · guruh" : " · shaxsiy"}
                          </span>
                        </td>
                        <td data-label="Status">
                          <StatusBadge status={task.status} />
                        </td>
                        <td className="muted numeric" data-label="Berilgan">
                          {formatDateTime(task.created_at)}
                        </td>
                        <td className="muted numeric" data-label="Yakunlangan">
                          {formatDateTime(task.done_at ?? task.cancelled_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                page={page}
                pageSize={pageSize}
                total={total}
                onPage={setPage}
                onPageSize={setPageSize}
              />
            </>
          ) : (
            <StateBlock
              title="Topshiriq topilmadi"
              description="Davr, status yoki chat filtrlarini o'zgartiring"
            />
          )}
        </Card>
      </div>

      {openTask !== null && <TaskDrawer taskId={openTask} onClose={() => setOpenTask(null)} />}
    </>
  );
}
