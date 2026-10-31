import type { PropsWithChildren, ReactNode } from "react";

type PanelProps = PropsWithChildren<{
  title?: string;
  action?: ReactNode;
  className?: string;
}>;

export default function Panel({ title, action, className = "", children }: PanelProps) {
  return (
    <section className={`rounded-lg border border-line bg-panel p-5 shadow-soft ${className}`}>
      {(title || action) && (
        <div className="mb-4 flex items-center justify-between gap-4">
          {title ? <h2 className="text-lg font-semibold text-ink">{title}</h2> : <span />}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

