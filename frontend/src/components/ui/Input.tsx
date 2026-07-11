import { forwardRef, type InputHTMLAttributes } from "react";

import { THEME } from "@/config/theme";
import { cn } from "@/utils/cn";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({ label, error, className, id, ...props }, ref) => {
  const inputId = id ?? label.toLowerCase().replace(/\s+/g, "-");

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium" htmlFor={inputId} style={{ color: THEME.colors.text }}>
        {label}
      </label>
      <input
        ref={ref}
        id={inputId}
        className={cn(
          "w-full rounded-xl border px-4 py-3 text-sm outline-none transition-all duration-200 focus:border-transparent focus:ring-2 focus:ring-[var(--accent)]",
          className,
        )}
        style={{
          backgroundColor: THEME.colors.surface,
          borderColor: error ? THEME.colors.error : THEME.colors.border,
          color: THEME.colors.text,
          borderRadius: THEME.radius.md,
        }}
        {...props}
      />
      {error ? (
        <p className="text-sm" style={{ color: THEME.colors.error }}>
          {error}
        </p>
      ) : null}
    </div>
  );
});

Input.displayName = "Input";
