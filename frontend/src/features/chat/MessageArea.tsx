import { useEffect, useRef } from "react";

import { EmptyState } from "@/components/ui/EmptyState";
import { Spinner } from "@/components/ui/Spinner";
import { useAssistant } from "@/hooks/useAssistant";
import { type ConversationDetail } from "@/types";

import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface MessageAreaProps {
  conversation: ConversationDetail | null;
  loading: boolean;
  isSending: boolean;
  compact?: boolean;
}

export function MessageArea({ conversation, loading, isSending, compact = false }: MessageAreaProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const { setDraftMessage } = useAssistant();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [conversation?.conversation_id, conversation?.messages.length]);

  if (loading) {
    return (
      <div className="flex min-h-[320px] items-center justify-center">
        <Spinner label="Loading conversation..." />
      </div>
    );
  }

  if (!conversation || conversation.messages.length === 0) {
    return (
      <div className="space-y-4">
        <EmptyState
          title="How can I help today?"
          description="Pick a suggestion or type your own question to begin."
        />
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-2">
          {[
            { label: "Attendance", prompt: "Explain my attendance." },
            { label: "Today's Timetable", prompt: "Show today's timetable." },
            { label: "Policies", prompt: "What is the attendance policy?" },
            { label: "Registered Courses", prompt: "Show my registered courses." },
          ].map((item) => (
            <button
              key={item.label}
              type="button"
              className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-left text-sm font-medium text-[var(--text)] transition-colors hover:bg-[var(--surface)]"
              onClick={() => setDraftMessage(item.prompt)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 flex-col gap-4">
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {conversation.messages.map((message) => (
          <MessageBubble key={message.message_id} message={message} />
        ))}
        {isSending ? <TypingIndicator /> : null}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
