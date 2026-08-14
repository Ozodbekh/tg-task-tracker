import { statusLabel } from "@/lib/filters";
import type { TaskStatus } from "@/types/domain";

export const STATUS_COLOR: Record<TaskStatus, string> = {
  open: "var(--open)",
  in_progress: "var(--progress)",
  done: "var(--done)",
  cancelled: "var(--cancelled)",
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  return (
    <span className={`badge badge-${status}`}>
      <span className="badge-dot" />
      {statusLabel(status)}
    </span>
  );
}
