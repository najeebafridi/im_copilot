import { type PropsWithChildren } from "react";

import { THEME } from "@/config/theme";
import { cn } from "@/utils/cn";

interface AlertProps extends PropsWithChildren {
  variant?: "error" | "warning" | "success";
  className?: string;
}

export function Alert({ variant = "error", className, children }: AlertProps) {
  const styleMap = {
    error: { backgroundColor: "rgba(220,38,38,0.08)", borderColor: "rgba(220,38,38,0.18)", color: THEME.colors.error },
    warning: { backgroundColor: "rgba(217,119,6,0.08)", borderColor: "rgba(217,119,6,0.18)", color: THEME.colors.warning },
    success: { backgroundColor: "rgba(21,128,61,0.08)", borderColor: "rgba(21,128,61,0.18)", color: THEME.colors.success },
  }[variant];

  return (
    <div className={cn("rounded-xl border px-4 py-3 text-sm", className)} style={styleMap}>
      {children}
    </div>
  );
}
