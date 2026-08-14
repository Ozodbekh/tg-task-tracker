import type { Bucket } from "@/types/domain";

const dateTime = new Intl.DateTimeFormat("uz-UZ", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

const dateOnly = new Intl.DateTimeFormat("uz-UZ", {
  day: "2-digit",
  month: "short",
  year: "numeric",
});

const number = new Intl.NumberFormat("uz-UZ");

export function formatDateTime(value: string | null): string {
  return value ? dateTime.format(new Date(value)) : "—";
}

export function formatDate(value: string | null): string {
  return value ? dateOnly.format(new Date(value)) : "—";
}

export function formatNumber(value: number): string {
  return number.format(value);
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`;
}

export function formatDuration(seconds: number | null): string {
  if (seconds === null) return "—";
  if (seconds < 60) return `${Math.round(seconds)} son.`;
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} daq.`;
  const hours = seconds / 3600;
  if (hours < 24) return `${hours.toFixed(1)} soat`;
  return `${(hours / 24).toFixed(1)} kun`;
}

export function formatRelative(value: string | null): string {
  if (!value) return "—";
  const diff = (Date.now() - new Date(value).getTime()) / 1000;
  if (diff < 60) return "hozirgina";
  if (diff < 3600) return `${Math.round(diff / 60)} daqiqa oldin`;
  if (diff < 86400) return `${Math.round(diff / 3600)} soat oldin`;
  if (diff < 2592000) return `${Math.round(diff / 86400)} kun oldin`;
  return formatDate(value);
}

export function formatBucket(value: string, bucket: Bucket): string {
  const date = new Date(value);
  if (bucket === "hour") {
    return new Intl.DateTimeFormat("uz-UZ", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  }
  if (bucket === "month") {
    return new Intl.DateTimeFormat("uz-UZ", {
      month: "short",
      year: "2-digit",
    }).format(date);
  }
  return new Intl.DateTimeFormat("uz-UZ", {
    day: "2-digit",
    month: "short",
  }).format(date);
}

export function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? "")
    .join("");
}

export function chatName(title: string | null, fallback: string): string {
  return title?.trim() ? title : fallback;
}
