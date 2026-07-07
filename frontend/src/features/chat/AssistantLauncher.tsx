import { Button } from "@/components/ui/Button";
import { MessageCirclePlus } from "lucide-react";
import { type AssistantMode } from "@/types";

interface AssistantLauncherProps {
  mode: AssistantMode;
  onActivate: () => void;
}

export function AssistantLauncher({ mode, onActivate }: AssistantLauncherProps) {
  return (
    <div className="fixed bottom-5 right-5 z-40">
      <Button
        type="button"
        className="h-14 w-14 rounded-full border border-slate-200 bg-slate-950 p-0 text-white shadow-2xl shadow-slate-950/20 transition-transform hover:-translate-y-0.5"
        onClick={onActivate}
        aria-label={mode === "CLOSED" ? "Open assistant" : "Assistant"}
        title="IM Copilot"
      >
        <MessageCirclePlus className="h-5 w-5" />
      </Button>
    </div>
  );
}
