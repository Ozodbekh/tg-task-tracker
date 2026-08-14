import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { FilterBar } from "@/components/FilterBar";
import { PageHeader } from "@/components/Layout";
import { Pagination } from "@/components/Pagination";
import { StatCard } from "@/components/StatCard";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { StatusLegend, StatusSplitBar } from "@/components/StatusSplitBar";
import { StackedBarChart } from "@/components/charts/StackedBarChart";
import { useFilters } from "@/hooks/FiltersContext";
import { usePagination } from "@/hooks/usePagination";
import { useResource } from "@/hooks/useResource";
import { periodLabel } from "@/lib/filters";
import { chatName, formatNumber, formatPercent, formatRelative } from "@/lib/format";

const TOP_CHATS = 10;

export function ChatsPage() {
  const { filters, setFilters, chats } = useFilters();
  const filterKey = JSON.stringify(filters);
  const { page, pageSize, setPage, setPageSize } = usePagination(filterKey);

  const overview = useResource(() => backend.overview(filters), [filterKey]);
  const top = useResource(
    () => backend.chatStats({ ...filters, page: 1, page_size: TOP_CHATS }),
    [filterKey],
  );
  const stats = useResource(
    () => backend.chatStats({ ...filters, page, page_size: pageSize }),
    [JSON.stringify({ filters, page, pageSize })],
  );

  const rows = stats.data?.items ?? [];

  return (
    <>
      <PageHeader
        title="Chat va guruhlar"
        subtitle={`${periodLabel(filters.period)} kesimida topshiriqlar manbasi`}
        filters={<FilterBar />}
      />

      <div className="content">
        <div className="grid grid-stats">
          <StatCard
            label="Faol manba"
            value={formatNumber(overview.data?.active_chats ?? 0)}
            hint={`${formatNumber(chats.length)} ta ro'yxatda`}
          />
          <StatCard
            label="Guruhlar"
            value={formatNumber(chats.filter((chat) => chat.type === "group").length)}
          />
          <StatCard
            label="Shaxsiy chatlar"
            value={formatNumber(chats.filter((chat) => chat.type === "private").length)}
          />
          <StatCard
            label="Aniqlanmagan xabarlar"
            value={formatNumber(overview.data?.unresolved ?? 0)}
            hint={`${formatNumber(overview.data?.total ?? 0)} ta topshiriqdan`}
          />
        </div>

        <Card
          title={`Eng faol ${TOP_CHATS} ta manba`}
          hint="Statuslar bo'yicha taqsimot"
          actions={<StatusLegend />}
        >
          {top.data?.items.length ? (
            <StackedBarChart
              data={top.data.items.map((row) => ({
                name: chatName(row.chat.title, `Chat ${row.chat.telegram_id}`),
                ...row.by_status,
              }))}
              height={360}
            />
          ) : top.loading ? (
            <Skeleton height={360} />
          ) : (
            <StateBlock title="Bu davrda ma'lumot yo'q" />
          )}
        </Card>

        <Card title="Chatlar ro'yxati" padded={false} hint="Qatorni bosib filtrga qo'ying">
          {stats.error ? (
            <StateBlock title="Yuklab bo'lmadi" description={stats.error} onRetry={stats.reload} />
          ) : stats.loading && !stats.data ? (
            <div style={{ padding: 18 }}>
              <Skeleton height={280} />
            </div>
          ) : rows.length ? (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Chat</th>
                      <th>Turi</th>
                      <th>Jami</th>
                      <th>Taqsimot</th>
                      <th>Bajarilish</th>
                      <th>Ishtirokchi</th>
                      <th>Aniqlanmagan</th>
                      <th>So'nggi topshiriq</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr
                        key={row.chat.id}
                        className="clickable"
                        onClick={() => setFilters({ chat_id: row.chat.id })}
                      >
                        <td>
                          <span className="cell-title">
                            {chatName(row.chat.title, `Chat ${row.chat.telegram_id}`)}
                          </span>
                        </td>
                        <td data-label="Turi">
                          <span className="badge badge-neutral">
                            {row.chat.type === "group" ? "Guruh" : "Shaxsiy"}
                          </span>
                        </td>
                        <td className="numeric" data-label="Jami">
                          {formatNumber(row.total)}
                        </td>
                        <td style={{ minWidth: 160 }} data-label="Taqsimot">
                          <StatusSplitBar counts={row.by_status} />
                        </td>
                        <td className="numeric" data-label="Bajarilish">
                          {formatPercent(row.completion_rate)}
                        </td>
                        <td className="numeric muted" data-label="Ishtirokchi">
                          {formatNumber(row.participants)}
                        </td>
                        <td className="numeric muted" data-label="Aniqlanmagan">
                          {formatNumber(row.unresolved)}
                        </td>
                        <td className="numeric muted" data-label="So'nggi topshiriq">
                          {formatRelative(row.last_task_at)}
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
            <StateBlock title="Chat topilmadi" />
          )}
        </Card>
      </div>
    </>
  );
}
