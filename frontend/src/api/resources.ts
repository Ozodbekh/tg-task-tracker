import { api } from "@/api/client";
import type { Filters } from "@/lib/filters";
import { filtersToQuery } from "@/lib/filters";
import type {
  Chat,
  ChatStats,
  Employee,
  EmployeeStats,
  Overview,
  Paginated,
  Session,
  Task,
  TaskDetail,
  TimeseriesPoint,
  UnresolvedMessage,
} from "@/types/domain";

export interface PageQuery extends Filters {
  page?: number;
  page_size?: number;
}

export interface TaskQuery extends PageQuery {
  search?: string;
  sort?: string;
}

function pageQuery(query: PageQuery): Record<string, string | number | undefined> {
  return {
    ...filtersToQuery(query),
    page: query.page,
    page_size: query.page_size,
  };
}

export const backend = {
  login: (username: string, password: string) =>
    api.post<Session>("/api/auth/login", { username, password }),
  logout: () => api.post<void>("/api/auth/logout"),
  me: () => api.get<Session>("/api/auth/me"),

  overview: (filters: Filters) => api.get<Overview>("/api/stats/overview", filtersToQuery(filters)),
  timeseries: (filters: Filters) =>
    api.get<TimeseriesPoint[]>("/api/stats/timeseries", filtersToQuery(filters)),
  employeeStats: (query: PageQuery) =>
    api.get<Paginated<EmployeeStats>>("/api/stats/employees", pageQuery(query)),
  chatStats: (query: PageQuery) =>
    api.get<Paginated<ChatStats>>("/api/stats/chats", pageQuery(query)),

  employees: () => api.get<Employee[]>("/api/employees"),
  employee: (id: number, filters: Filters) =>
    api.get<EmployeeStats>(`/api/employees/${id}/stats`, filtersToQuery(filters)),
  chats: () => api.get<Chat[]>("/api/chats"),

  tasks: (query: TaskQuery) =>
    api.get<Paginated<Task>>("/api/tasks", {
      ...pageQuery(query),
      search: query.search,
      sort: query.sort,
    }),
  task: (id: number) => api.get<TaskDetail>(`/api/tasks/${id}`),
  unresolved: (query: PageQuery) =>
    api.get<Paginated<UnresolvedMessage>>("/api/unresolved", pageQuery(query)),
};
