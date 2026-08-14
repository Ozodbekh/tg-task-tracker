import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  hint?: string;
  actions?: ReactNode;
  padded?: boolean;
  children: ReactNode;
}

export function Card({ title, hint, actions, padded = true, children }: CardProps) {
  return (
    <section className="card">
      {(title || actions) && (
        <header className="card-header">
          <div className="stack">
            {title && <h2 className="card-title">{title}</h2>}
            {hint && <p className="card-hint">{hint}</p>}
          </div>
          {actions}
        </header>
      )}
      {padded ? <div className="card-body">{children}</div> : children}
    </section>
  );
}
