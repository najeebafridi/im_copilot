import { Card } from "@/components/ui/Card";
import { type ConversationDetail } from "@/types";

import { AssistantInput } from "./AssistantInput";
import { MessageArea } from "./MessageArea";

interface ConversationWorkspaceProps {
  conversation: ConversationDetail | null;
  loading: boolean;
  isSending: boolean;
  compact?: boolean;
}

export function ConversationWorkspace({ conversation, loading, isSending, compact = false }: ConversationWorkspaceProps) {
  return (
    <div className="flex h-full min-h-0 flex-1 flex-col gap-3 overflow-hidden p-4 pb-[calc(env(safe-area-inset-bottom)+1rem)]">
      <Card className="flex min-h-0 flex-1 flex-col overflow-hidden border-[var(--border)]">
        <div className="border-b border-[var(--border)] px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">Conversation Workspace</p>
          <h3 className="mt-1 text-base font-semibold text-[var(--text)]">
            {conversation ? conversation.title : "Welcome to IM Copilot"}
          </h3>
        </div>

        <div className="min-h-0 flex-1 overflow-hidden px-4 py-3 pb-5">
          <MessageArea conversation={conversation} loading={loading} isSending={isSending} compact={compact} />
        </div>
      </Card>

      <div className="shrink-0">
        <AssistantInput />
      </div>
    </div>
  );
}
