import { useFilters } from "@/hooks/FiltersContext";
import { CHAT_TYPES, PERIODS, STATUSES, activeFilterCount } from "@/lib/filters";
import type { ChatType, TaskStatus } from "@/types/domain";

interface FilterBarProps {
  showStatus?: boolean;
  showChat?: boolean;
  showEmployee?: boolean;
}

export function FilterBar({
  showStatus = true,
  showChat = true,
  showEmployee = true,
}: FilterBarProps) {
  const { filters, setFilters, reset, chats, employees } = useFilters();
  const groups = chats.filter((chat) => chat.type === "group");
  const privates = chats.filter((chat) => chat.type === "private");

  return (
    <div className="filters">
      <div className="segmented" role="group" aria-label="Davr">
        {PERIODS.map((period) => (
          <button
            key={period.value}
            type="button"
            className={filters.period === period.value ? "active" : ""}
            onClick={() => setFilters({ period: period.value })}
          >
            {period.short}
          </button>
        ))}
      </div>

      {showStatus && (
        <select
          className="select"
          value={filters.status ?? ""}
          onChange={(event) =>
            setFilters({
              status: (event.target.value || null) as TaskStatus | null,
            })
          }
          aria-label="Status"
        >
          <option value="">Barcha statuslar</option>
          {STATUSES.map((status) => (
            <option key={status.value} value={status.value}>
              {status.label}
            </option>
          ))}
        </select>
      )}

      {showChat && (
        <>
          <select
            className="select"
            value={filters.chat_type ?? ""}
            onChange={(event) =>
              setFilters({
                chat_type: (event.target.value || null) as ChatType | null,
                chat_id: null,
              })
            }
            aria-label="Chat turi"
          >
            <option value="">Barcha turlar</option>
            {CHAT_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>

          <select
            className="select"
            value={filters.chat_id ?? ""}
            onChange={(event) =>
              setFilters({
                chat_id: event.target.value ? Number(event.target.value) : null,
              })
            }
            aria-label="Chat"
          >
            <option value="">Barcha chatlar</option>
            <optgroup label="Guruhlar">
              {groups.map((chat) => (
                <option key={chat.id} value={chat.id}>
                  {chat.title ?? `Guruh ${chat.telegram_id}`}
                </option>
              ))}
            </optgroup>
            <optgroup label="Shaxsiy chatlar">
              {privates.map((chat) => (
                <option key={chat.id} value={chat.id}>
                  {chat.title ?? `Chat ${chat.telegram_id}`}
                </option>
              ))}
            </optgroup>
          </select>
        </>
      )}

      {showEmployee && (
        <select
          className="select"
          value={filters.employee_id ?? ""}
          onChange={(event) =>
            setFilters({
              employee_id: event.target.value ? Number(event.target.value) : null,
            })
          }
          aria-label="Xodim"
        >
          <option value="">Barcha xodimlar</option>
          {employees.map((employee) => (
            <option key={employee.id} value={employee.id}>
              {employee.name}
            </option>
          ))}
        </select>
      )}

      {activeFilterCount(filters) > 0 && (
        <button type="button" className="ghost-button" onClick={reset}>
          Filtrlarni tozalash ({activeFilterCount(filters)})
        </button>
      )}
    </div>
  );
}
