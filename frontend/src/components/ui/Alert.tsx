import { type PropsWithChildren } from "react";

import { THEME } from "@/config/theme";
import { cn } from "@/utils/cn";

interface AlertProps extends PropsWithChildren {
  variant?: "error" | "warning" | "success";
  className?: string;
}

export function Alert({ variant = "error", className, children }: AlertProps) {
  const styleMap = {
    error: { backgroundColor: "#FEF3F2", borderColor: "#FDA29B", color: THEME.colors.error },
    warning: { backgroundColor: "#FFFAEB", borderColor: "#FEC84B", color: THEME.colors.warning },
    success: { backgroundColor: "#ECFDF3", borderColor: "#ABEFC6", color: THEME.colors.success },
  }[variant];

  return (
    <div className={cn("rounded-xl border px-4 py-3 text-sm", className)} style={styleMap}>
      {children}
    </div>
  );
}
