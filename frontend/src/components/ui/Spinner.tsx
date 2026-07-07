interface SpinnerProps {
  label?: string;
}

export function Spinner({ label = "Loading..." }: SpinnerProps) {
  return (
    <div className="flex items-center gap-3 text-sm text-slate-600" role="status" aria-live="polite">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
      <span>{label}</span>
    </div>
  );
}
