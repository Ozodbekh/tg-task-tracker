interface StateBlockProps {
  title: string;
  description?: string;
  onRetry?: () => void;
}

export function StateBlock({ title, description, onRetry }: StateBlockProps) {
  return (
    <div className="state">
      <p className="state-title">{title}</p>
      {description && <p>{description}</p>}
      {onRetry && (
        <button type="button" className="ghost-button" onClick={onRetry}>
          Qayta urinish
        </button>
      )}
    </div>
  );
}

export function Skeleton({ height = 120 }: { height?: number }) {
  return <div className="skeleton" style={{ height }} />;
}
