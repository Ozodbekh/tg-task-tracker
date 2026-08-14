import { useEffect, useState } from "react";

interface PaginationState {
  page: number;
  pageSize: number;
  setPage: (page: number) => void;
  setPageSize: (size: number) => void;
}

export function usePagination(resetKey: string, initialSize = 20): PaginationState {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialSize);

  useEffect(() => setPage(1), [resetKey, pageSize]);

  return {
    page,
    pageSize,
    setPage,
    setPageSize,
  };
}

export function useDebounced<T>(value: T, delay = 300): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debounced;
}
