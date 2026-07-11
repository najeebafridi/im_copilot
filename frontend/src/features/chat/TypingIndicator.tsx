import { Spinner } from "@/components/ui/Spinner";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--muted)]">
      <Spinner label="IM Copilot is thinking..." />
    </div>
  );
}
