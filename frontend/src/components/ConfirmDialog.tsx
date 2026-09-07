import { useEffect } from "react";

interface ConfirmDialogProps {
  title: string;
  description: string;
  confirmLabel: string;
  danger?: boolean;
  pending?: boolean;
  error?: string | null;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmDialog({
  title,
  description,
  confirmLabel,
  danger = false,
  pending = false,
  error,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape" && !pending) onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, pending]);

  return (
    <div className="dialog-scrim" role="presentation" onClick={() => !pending && onCancel()}>
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="dialog"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 className="card-title">{title}</h2>
        <p className="muted">{description}</p>

        {error && <p className="error-text">{error}</p>}

        <div className="dialog-actions">
          <button type="button" className="ghost-button" disabled={pending} onClick={onCancel}>
            Bekor qilish
          </button>
          <button
            type="button"
            className={danger ? "primary-button danger-button" : "primary-button"}
            disabled={pending}
            onClick={onConfirm}
          >
            {pending ? "Bajarilmoqda…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
