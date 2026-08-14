import { useEffect } from "react";

import { backend } from "@/api/resources";
import { StateBlock, Skeleton } from "@/components/StateBlock";
import { STATUS_COLOR, StatusBadge } from "@/components/StatusBadge";
import { useResource } from "@/hooks/useResource";
import { statusLabel } from "@/lib/filters";
import { chatName, formatDateTime, formatDuration } from "@/lib/format";

interface TaskDrawerProps {
  taskId: number;
  onClose: () => void;
}

export function TaskDrawer({ taskId, onClose }: TaskDrawerProps) {
  const task = useResource(() => backend.task(taskId), [taskId]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const data = task.data;
  const duration =
    data?.done_at && data.created_at
      ? (new Date(data.done_at).getTime() - new Date(data.created_at).getTime()) / 1000
      : null;

  return (
    <div className="drawer-scrim" role="presentation" onClick={onClose}>
      <aside
        role="dialog"
        aria-label="Topshiriq tafsilotlari"
        className="drawer"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="row-between">
          <h2 className="page-title">Topshiriq #{taskId}</h2>
          <button type="button" className="ghost-button" onClick={onClose}>
            Yopish
          </button>
        </div>

        {task.loading && !data ? (
          <Skeleton height={320} />
        ) : task.error ? (
          <StateBlock title="Yuklab bo'lmadi" description={task.error} onRetry={task.reload} />
        ) : (
          data && (
            <>
              <p style={{ fontSize: 15, fontWeight: 550 }}>{data.text}</p>
              <StatusBadge status={data.status} />

              <div className="detail-grid">
                <div className="detail-item">
                  <span className="detail-label">Ijrochi</span>
                  <span className="detail-value">{data.employee.name}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Chat</span>
                  <span className="detail-value">
                    {chatName(data.chat.title, `Chat ${data.chat.telegram_id}`)}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Turi</span>
                  <span className="detail-value">
                    {data.chat.type === "group" ? "Guruh" : "Shaxsiy chat"}
                  </span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Berilgan</span>
                  <span className="detail-value">{formatDateTime(data.created_at)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Boshlangan</span>
                  <span className="detail-value">{formatDateTime(data.started_at)}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Sarflangan vaqt</span>
                  <span className="detail-value">{formatDuration(duration)}</span>
                </div>
              </div>

              {data.message_link && (
                <a className="link" href={data.message_link} target="_blank" rel="noreferrer">
                  Telegramdagi xabarni ochish →
                </a>
              )}

              <div className="stack" style={{ gap: 12 }}>
                <h3 className="card-title">Tarix</h3>
                <div className="timeline">
                  {data.events.map((event, index) => (
                    <div key={event.id} className="timeline-item">
                      <div className="timeline-rail">
                        <span
                          className="timeline-dot"
                          style={{ background: STATUS_COLOR[event.status] }}
                        />
                        {index < data.events.length - 1 && <span className="timeline-line" />}
                      </div>
                      <div className="timeline-body">
                        <span style={{ fontWeight: 550 }}>{statusLabel(event.status)}</span>
                        <span className="cell-sub">
                          {event.actor_name} · {formatDateTime(event.created_at)}
                        </span>
                        {event.text && <span className="muted">{event.text}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )
        )}
      </aside>
    </div>
  );
}
