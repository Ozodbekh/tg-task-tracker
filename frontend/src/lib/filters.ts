import type { Bucket, ChatType, Period, TaskStatus } from "@/types/domain";

export interface Filters {
  period: Period;
  bucket?: Bucket;
  status?: TaskStatus | null;
  chat_id?: number | null;
  chat_type?: ChatType | null;
  employee_id?: number | null;
}

export const PERIODS: { value: Period; label: string; short: string }[] = [
  { value: "day", label: "Bugun", short: "Kun" },
  { value: "week", label: "Hafta", short: "Hafta" },
  { value: "month", label: "Oy", short: "Oy" },
  { value: "quarter", label: "3 oy", short: "3 oy" },
  { value: "9months", label: "9 oy", short: "9 oy" },
  { value: "year", label: "1 yil", short: "Yil" },
  { value: "all", label: "Butun davr", short: "Hammasi" },
];

export const STATUSES: { value: TaskStatus; label: string }[] = [
  { value: "open", label: "Ochiq" },
  { value: "in_progress", label: "Jarayonda" },
  { value: "on_hold", label: "To'xtatib turilgan" },
  { value: "blocked", label: "Bloklangan" },
  { value: "done", label: "Bajarilgan" },
  { value: "cancelled", label: "Bekor qilingan" },
];

export const CHAT_TYPES: { value: ChatType; label: string }[] = [
  { value: "private", label: "Shaxsiy chat" },
  { value: "group", label: "Guruh" },
];

const DEFAULT_BUCKET: Record<Period, Bucket> = {
  day: "hour",
  week: "day",
  month: "day",
  quarter: "week",
  "9months": "month",
  year: "month",
  all: "month",
};

export const DEFAULT_FILTERS: Filters = {
  period: "month",
  status: null,
  chat_id: null,
  chat_type: null,
  employee_id: null,
};

export function bucketFor(period: Period): Bucket {
  return DEFAULT_BUCKET[period];
}

export function filtersToQuery(filters: Filters): Record<string, string | number | undefined> {
  return {
    period: filters.period,
    bucket: filters.bucket ?? bucketFor(filters.period),
    status: filters.status ?? undefined,
    chat_id: filters.chat_id ?? undefined,
    chat_type: filters.chat_type ?? undefined,
    employee_id: filters.employee_id ?? undefined,
  };
}

export function periodLabel(period: Period): string {
  return PERIODS.find((item) => item.value === period)?.label ?? period;
}

export function statusLabel(status: TaskStatus): string {
  return STATUSES.find((item) => item.value === status)?.label ?? status;
}

export function activeFilterCount(filters: Filters): number {
  return [filters.status, filters.chat_id, filters.chat_type, filters.employee_id].filter(Boolean)
    .length;
}
