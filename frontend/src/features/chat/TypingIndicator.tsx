import { Spinner } from "@/components/ui/Spinner";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600">
      <Spinner label="IM Copilot is thinking..." />
    </div>
  );
}
