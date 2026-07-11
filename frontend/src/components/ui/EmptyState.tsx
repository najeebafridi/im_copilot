import { type ReactNode } from "react";

import { THEME } from "@/config/theme";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 text-center shadow-[0_8px_24px_rgba(16,36,59,0.06)]">
      <h3 className="text-lg font-semibold" style={{ color: THEME.colors.text }}>
        {title}
      </h3>
      <p className="mt-2 text-sm" style={{ color: THEME.colors.mutedText }}>
        {description}
      </p>
      {action ? <div className="mt-4 flex justify-center">{action}</div> : null}
    </div>
  );
}
