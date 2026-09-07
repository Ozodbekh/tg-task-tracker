import { createContext, useContext, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { backend } from "@/api/resources";
import { DEFAULT_FILTERS, type Filters } from "@/lib/filters";
import { useResource } from "@/hooks/useResource";
import type { Chat, Employee } from "@/types/domain";

interface FiltersValue {
  filters: Filters;
  setFilters: (patch: Partial<Filters>) => void;
  reset: () => void;
  chats: Chat[];
  employees: Employee[];
  reloadEmployees: () => void;
}

const FiltersContext = createContext<FiltersValue | null>(null);

export function FiltersProvider({ children }: { children: ReactNode }) {
  const [filters, setState] = useState<Filters>(DEFAULT_FILTERS);
  const chats = useResource(() => backend.chats(), []);
  const employees = useResource(() => backend.employees(), []);

  const value = useMemo<FiltersValue>(
    () => ({
      filters,
      setFilters: (patch) => setState((current) => ({ ...current, ...patch })),
      reset: () => setState(DEFAULT_FILTERS),
      chats: chats.data ?? [],
      employees: employees.data ?? [],
      reloadEmployees: employees.reload,
    }),
    [filters, chats.data, employees.data, employees.reload],
  );

  return <FiltersContext value={value}>{children}</FiltersContext>;
}

export function useFilters(): FiltersValue {
  const value = useContext(FiltersContext);
  if (!value) throw new Error("useFilters must be used inside FiltersProvider");
  return value;
}
