import { useMemo, useState } from "react";
import { Plus, Settings2, Trash2 } from "lucide-react";

import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { type ConversationSummary } from "@/types";
import { cn } from "@/utils/cn";

interface ConversationSidebarProps {
  conversations: ConversationSummary[];
  currentConversationId: string | null;
  loading: boolean;
  error: string | null;
  compact?: boolean;
  onCreateConversation: () => Promise<void>;
  onSelectConversation: (conversationId: string) => Promise<void>;
  onDeleteConversation: (conversationId: string) => Promise<void>;
  onSettings: () => void;
}

export function ConversationSidebar({
  conversations,
  currentConversationId,
  loading,
  error,
  compact = false,
  onCreateConversation,
  onSelectConversation,
  onDeleteConversation,
  onSettings,
}: ConversationSidebarProps) {
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);
  const pendingConversation = conversations.find((item) => item.conversation_id === pendingDeleteId) ?? null;
  const recentConversations = useMemo(() => [...conversations].sort((left, right) => {
    return new Date(right.last_activity).getTime() - new Date(left.last_activity).getTime();
  }), [conversations]);

  async function handleCreateConversation(): Promise<void> {
    try {
      await onCreateConversation();
    } catch {
      // provider stores UI error
    }
  }

  async function handleDelete(): Promise<void> {
    if (!pendingDeleteId) {
      return;
    }

    try {
      await onDeleteConversation(pendingDeleteId);
      setPendingDeleteId(null);
    } catch {
      // provider stores UI error
    }
  }

  return (
    <>
      <aside className="flex h-full min-h-0 flex-col bg-slate-50/80">
        <div className={cn("border-b border-slate-200", compact ? "p-2" : "p-3")}>
          <Button type="button" className="w-full justify-start gap-2 rounded-2xl" onClick={() => void handleCreateConversation()}>
            <Plus className="h-4 w-4" />
            New Conversation
          </Button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-2 py-2">
          {loading ? (
            <div className="flex min-h-[160px] items-center justify-center">
              <Spinner label="Loading..." />
            </div>
          ) : error ? (
            <Alert variant="error">
              <div className="space-y-2">
                <p>{error}</p>
              </div>
            </Alert>
          ) : recentConversations.length === 0 ? (
            <EmptyState title="No chats yet" description="Create a new chat to begin." />
          ) : (
            <div className="space-y-1">
              {recentConversations.map((conversation) => {
                const active = conversation.conversation_id === currentConversationId;
                return (
                  <div
                    key={conversation.conversation_id}
                    className={cn(
                      "group flex w-full items-center justify-between gap-2 rounded-xl px-2.5 py-2 text-left transition-colors",
                      active ? "bg-slate-900 text-white" : "hover:bg-white",
                    )}
                    aria-current={active ? "page" : undefined}
                  >
                    <button
                      type="button"
                      className="min-w-0 flex-1 text-left"
                      onClick={() => void onSelectConversation(conversation.conversation_id).catch(() => {})}
                    >
                      <p className="truncate text-sm font-medium">{conversation.title}</p>
                    </button>
                    <span
                      className={cn(
                        "h-2 w-2 shrink-0 rounded-full",
                        active ? "bg-white" : "bg-slate-300 group-hover:bg-slate-400",
                      )}
                      aria-hidden="true"
                    />
                    <button
                      type="button"
                      className={cn(
                        "inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-slate-500 opacity-0 transition-opacity group-hover:opacity-100",
                        active ? "border-white/20 bg-white/10 text-white" : "border-slate-200 bg-white",
                      )}
                      onClick={() => setPendingDeleteId(conversation.conversation_id)}
                      aria-label={`Delete ${conversation.title}`}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        <div className="border-t border-slate-200 p-2">
          <button
            type="button"
            className="flex w-full items-center gap-2 rounded-xl px-2.5 py-2 text-sm text-slate-600 transition-colors hover:bg-white hover:text-slate-900"
            onClick={onSettings}
          >
            <Settings2 className="h-4 w-4" />
            Settings
          </button>
        </div>
      </aside>

      {pendingConversation ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Delete Conversation?</p>
            <h4 className="mt-2 text-xl font-semibold text-slate-900">{pendingConversation.title}</h4>
            <p className="mt-2 text-sm leading-6 text-slate-600">This action cannot be undone.</p>

            <div className="mt-6 flex flex-wrap justify-end gap-3">
              <Button variant="outline" type="button" onClick={() => setPendingDeleteId(null)}>
                Cancel
              </Button>
              <Button variant="danger" type="button" onClick={() => void handleDelete()}>
                Delete
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
