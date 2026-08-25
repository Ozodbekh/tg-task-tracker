export type TaskStatus = "open" | "in_progress" | "on_hold" | "blocked" | "done" | "cancelled";

export type ChatType = "private" | "group";

export type Period = "day" | "week" | "month" | "quarter" | "9months" | "year" | "all";

export type Bucket = "hour" | "day" | "week" | "month";

export interface Employee {
  id: number;
  telegram_id: number;
  name: string;
  created_at: string;
}

export interface Chat {
  id: number;
  telegram_id: number;
  type: ChatType;
  title: string | null;
  created_at: string;
}

export interface Task {
  id: number;
  text: string;
  status: TaskStatus;
  message_id: number;
  message_link: string | null;
  employee: Employee;
  chat: Chat;
  created_at: string;
  started_at: string | null;
  done_at: string | null;
  cancelled_at: string | null;
}

export interface TaskEvent {
  id: number;
  status: TaskStatus;
  actor_name: string;
  message_id: number;
  text: string;
  created_at: string;
}

export interface TaskDetail extends Task {
  events: TaskEvent[];
}

export interface UnresolvedMessage {
  id: number;
  chat: Chat;
  message_id: number;
  message_link: string | null;
  text: string;
  created_at: string;
}

export interface StatusCounts {
  open: number;
  in_progress: number;
  on_hold: number;
  blocked: number;
  done: number;
  cancelled: number;
}

export interface Overview {
  total: number;
  by_status: StatusCounts;
  completion_rate: number;
  avg_completion_seconds: number | null;
  avg_response_seconds: number | null;
  overdue_open: number;
  unresolved: number;
  active_employees: number;
  active_chats: number;
  previous: {
    total: number;
    done: number;
    completion_rate: number;
  } | null;
}

export interface TimeseriesPoint {
  bucket: string;
  created: number;
  done: number;
  in_progress: number;
  cancelled: number;
}

export interface EmployeeStats {
  employee: Employee;
  total: number;
  by_status: StatusCounts;
  completion_rate: number;
  avg_completion_seconds: number | null;
  avg_response_seconds: number | null;
  last_activity_at: string | null;
}

export interface ChatStats {
  chat: Chat;
  total: number;
  by_status: StatusCounts;
  completion_rate: number;
  unresolved: number;
  participants: number;
  last_task_at: string | null;
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Session {
  username: string;
}
