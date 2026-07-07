import { Button } from "@/components/ui/Button";
import { THEME } from "@/config/theme";
import { cn } from "@/utils/cn";

import { type ConversationSummary } from "@/types";

import { getConversationTypeLabel } from "./conversationGrouping";

interface ConversationCardProps {
  conversation: ConversationSummary;
  active: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

function getTypeMark(conversationType: ConversationSummary["conversation_type"]): string {
  return getConversationTypeLabel(conversationType).slice(0, 1).toUpperCase();
}

export function ConversationCard({ conversation, active, onSelect, onDelete }: ConversationCardProps) {
  return (
    <div
      className={cn(
        "rounded-xl border p-2.5 transition-colors",
        active ? "bg-slate-900 text-white" : "bg-white hover:bg-slate-50",
      )}
      style={{ borderColor: active ? THEME.colors.primary : THEME.colors.border }}
    >
      <button
        type="button"
        className="flex w-full items-start gap-3 text-left"
        onClick={onSelect}
        aria-current={active ? "page" : undefined}
      >
        <div
          className={cn(
            "flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-sm font-semibold",
            active ? "bg-white/10 text-white" : "bg-slate-100 text-slate-700",
          )}
        >
          {getTypeMark(conversation.conversation_type)}
        </div>
        <div className="min-w-0 flex-1 space-y-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className={cn("truncate text-sm font-semibold", active ? "text-white" : "text-slate-900")}>
                {conversation.title}
              </p>
              <p className={cn("text-xs", active ? "text-slate-300" : "text-slate-500")}>
                {getConversationTypeLabel(conversation.conversation_type)}
              </p>
            </div>
            <span className={cn("mt-1 h-2.5 w-2.5 rounded-full", active ? "bg-emerald-400" : "bg-slate-300")} />
          </div>
          <div className={cn("flex flex-wrap gap-3 text-xs", active ? "text-slate-300" : "text-slate-500")}>
            <span>{conversation.message_count} messages</span>
            <span>{new Date(conversation.last_activity).toLocaleDateString()}</span>
          </div>
        </div>
      </button>

      <div className="mt-2 flex justify-end">
        <Button variant="outline" type="button" size="sm" onClick={onDelete} aria-label={`Delete ${conversation.title}`}>
          Delete
        </Button>
      </div>
    </div>
  );
}
