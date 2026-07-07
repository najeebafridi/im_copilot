import { type PropsWithChildren } from "react";

import { cn } from "@/utils/cn";

interface CardProps extends PropsWithChildren {
  className?: string;
}

export function Card({ children, className }: CardProps) {
  return (
    <div
      className={cn("rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-[0_8px_24px_rgba(16,36,59,0.08)]", className)}
    >
      {children}
    </div>
  );
}
