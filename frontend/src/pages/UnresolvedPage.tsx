import { backend } from "@/api/resources";
import { Card } from "@/components/Card";
import { FilterBar } from "@/components/FilterBar";
import { PageHeader } from "@/components/Layout";
import { Pagination } from "@/components/Pagination";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { useFilters } from "@/hooks/FiltersContext";
import { usePagination } from "@/hooks/usePagination";
import { useResource } from "@/hooks/useResource";
import { chatName, formatDateTime } from "@/lib/format";

export function UnresolvedPage() {
  const { filters } = useFilters();
  const filterKey = JSON.stringify(filters);
  const { page, pageSize, setPage, setPageSize } = usePagination(filterKey);
  const messages = useResource(
    () => backend.unresolved({ ...filters, page, page_size: pageSize }),
    [JSON.stringify({ filters, page, pageSize })],
  );

  return (
    <>
      <PageHeader
        title="Aniqlanmagan xabarlar"
        subtitle="#task bor, lekin ijrochi aniqlanmagan xabarlar"
        filters={<FilterBar showStatus={false} showEmployee={false} />}
      />

      <div className="content">
        <Card padded={false}>
          {messages.error ? (
            <StateBlock
              title="Yuklab bo'lmadi"
              description={messages.error}
              onRetry={messages.reload}
            />
          ) : messages.loading && !messages.data ? (
            <div style={{ padding: 18 }}>
              <Skeleton height={240} />
            </div>
          ) : messages.data?.items.length ? (
            <>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Xabar</th>
                      <th>Chat</th>
                      <th>Vaqti</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {messages.data.items.map((item) => (
                      <tr key={item.id}>
                        <td>
                          <span className="cell-title">{item.text}</span>
                        </td>
                        <td className="muted" data-label="Chat">
                          {chatName(item.chat.title, `Chat ${item.chat.telegram_id}`)}
                        </td>
                        <td className="muted numeric" data-label="Vaqti">
                          {formatDateTime(item.created_at)}
                        </td>
                        <td>
                          {item.message_link && (
                            <a
                              className="link"
                              href={item.message_link}
                              target="_blank"
                              rel="noreferrer"
                            >
                              Telegramda ochish →
                            </a>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination
                page={page}
                pageSize={pageSize}
                total={messages.data.total}
                onPage={setPage}
                onPageSize={setPageSize}
              />
            </>
          ) : (
            <StateBlock title="Hammasi joyida" description="Aniqlanmagan xabarlar yo'q" />
          )}
        </Card>
      </div>
    </>
  );
}
