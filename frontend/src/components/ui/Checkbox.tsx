import { type InputHTMLAttributes } from "react";

import { THEME } from "@/config/theme";

interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, "type"> {
  label: string;
}

export function Checkbox({ label, ...props }: CheckboxProps) {
  return (
    <label className="flex items-center gap-3 text-sm" style={{ color: THEME.colors.text }}>
      <input type="checkbox" className="h-4 w-4 accent-[var(--accent)]" {...props} />
      <span>{label}</span>
    </label>
  );
}
