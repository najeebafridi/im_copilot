import { type PropsWithChildren } from "react";

import { cn } from "@/utils/cn";

interface PageCardProps extends PropsWithChildren {
  className?: string;
}

export function PageCard({ children, className }: PageCardProps) {
  return (
    <section
      className={cn("rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[0_8px_24px_rgba(16,36,59,0.08)]", className)}
    >
      {children}
    </section>
  );
}
