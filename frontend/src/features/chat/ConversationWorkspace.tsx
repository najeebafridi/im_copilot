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
    <div className="flex min-h-0 flex-1 flex-col gap-3 p-4 pb-10">
      <Card className="flex min-h-0 flex-1 flex-col overflow-hidden border-slate-200">
        <div className="border-b border-slate-200 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Conversation Workspace</p>
          <h3 className="mt-1 text-base font-semibold text-slate-900">
            {conversation ? conversation.title : "Welcome to IM Copilot"}
          </h3>
        </div>

        <div className="min-h-0 flex-1 overflow-hidden px-4 py-3 pb-5">
          <MessageArea conversation={conversation} loading={loading} isSending={isSending} compact={compact} />
        </div>
      </Card>

      <div className="pb-8">
        <AssistantInput />
      </div>
    </div>
  );
}
