import { formatNumber } from "@/lib/format";

export const PAGE_SIZES = [20, 50, 100];

interface PaginationProps {
  page: number;
  pageSize: number;
  total: number;
  onPage: (page: number) => void;
  onPageSize?: (size: number) => void;
}

export function Pagination({ page, pageSize, total, onPage, onPageSize }: PaginationProps) {
  const lastPage = Math.max(1, Math.ceil(total / pageSize));
  const from = total === 0 ? 0 : (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);

  return (
    <div className="pagination">
      <span>
        {formatNumber(total)} tadan {formatNumber(from)}–{formatNumber(to)} ko'rsatilmoqda
      </span>

      <div className="row">
        {onPageSize && (
          <select
            className="select"
            value={pageSize}
            onChange={(event) => onPageSize(Number(event.target.value))}
            aria-label="Sahifadagi qatorlar"
          >
            {PAGE_SIZES.map((size) => (
              <option key={size} value={size}>
                {size} ta
              </option>
            ))}
          </select>
        )}
        <button
          type="button"
          className="ghost-button"
          disabled={page <= 1}
          onClick={() => onPage(page - 1)}
        >
          ← Oldingi
        </button>
        <span className="numeric">
          {page} / {lastPage}
        </span>
        <button
          type="button"
          className="ghost-button"
          disabled={page >= lastPage}
          onClick={() => onPage(page + 1)}
        >
          Keyingi →
        </button>
      </div>
    </div>
  );
}
