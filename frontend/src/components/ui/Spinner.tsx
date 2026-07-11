interface SpinnerProps {
  label?: string;
}

export function Spinner({ label = "Loading..." }: SpinnerProps) {
  return (
    <div className="flex items-center gap-3 text-sm text-[var(--muted)]" role="status" aria-live="polite">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-[var(--border)] border-t-[var(--accent)]" />
      <span>{label}</span>
    </div>
  );
}
