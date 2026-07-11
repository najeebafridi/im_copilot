import { useMemo, useState, type KeyboardEvent } from "react";
import { Send } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { useAssistant } from "@/hooks/useAssistant";
import { useConversation } from "@/hooks/useConversation";
import { Alert } from "@/components/ui/Alert";
import { Spinner } from "@/components/ui/Spinner";

export function AssistantInput() {
  const { draftMessage, setDraftMessage } = useAssistant();
  const { sendMessage, isSending, error } = useConversation();
  const [localError, setLocalError] = useState<string | null>(null);
  const trimmed = useMemo(() => draftMessage.trim(), [draftMessage]);

  async function handleSend(): Promise<void> {
    if (!trimmed || isSending) {
      return;
    }

    setLocalError(null);
    try {
      await sendMessage(trimmed);
      setDraftMessage("");
    } catch (submitError) {
      setLocalError(submitError instanceof Error ? submitError.message : "Unable to send message.");
    }
  }

  return (
    <form
      className="shrink-0 space-y-2 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-3"
      onSubmit={(event) => {
        event.preventDefault();
        void handleSend();
      }}
    >
      <div className="space-y-1.5">
        <div className="flex items-center justify-between gap-3">
          <label className="text-xs font-medium text-[var(--text)]" htmlFor="assistant-message">
            How can I help today?
          </label>
          <span className="text-xs text-[var(--muted)]">{draftMessage.length} / 500</span>
        </div>
        <textarea
          id="assistant-message"
          className="min-h-[72px] w-full resize-none rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2.5 text-sm leading-6 text-[var(--text)] outline-none"
          placeholder="Ask about attendance, timetable, policies, or your courses."
          value={draftMessage}
          onChange={(event) => setDraftMessage(event.target.value)}
          onKeyDown={(event: KeyboardEvent<HTMLTextAreaElement>) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void handleSend();
            }
          }}
          disabled={isSending}
        />
      </div>

      {(localError || error) ? (
        <Alert variant="error" className="text-sm">
          {localError ?? error}
        </Alert>
      ) : null}

      <div className="flex items-center justify-end gap-2">
        {isSending ? <Spinner label="Sending..." /> : null}
        <Button type="submit" loading={isSending} disabled={!trimmed || isSending} className="h-10 px-4">
          <Send className="mr-2 h-4 w-4" />
          Send
        </Button>
      </div>
    </form>
  );
}
