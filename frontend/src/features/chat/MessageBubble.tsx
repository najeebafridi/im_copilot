import { useMemo, useState } from "react";
import { Check, Copy } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { cn } from "@/utils/cn";
import { type ConversationMessage } from "@/types";

import { MarkdownContent } from "./MarkdownContent";

interface MessageBubbleProps {
  message: ConversationMessage;
}

function extractCitations(content: string): { body: string; citations: string[] } {
  const markerPatterns = [/^citations:\s*$/im, /^sources:\s*$/im];
  for (const pattern of markerPatterns) {
    const match = content.match(pattern);
    if (!match || match.index === undefined) {
      continue;
    }

    const body = content.slice(0, match.index).trim();
    const citationBlock = content.slice(match.index + match[0].length).trim();
    const citations = citationBlock
      .split(/\n+/)
      .map((line) => line.replace(/^[-*]\s*/, "").trim())
      .filter(Boolean);
    return { body, citations };
  }

  return { body: content, citations: [] };
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";
  const [copied, setCopied] = useState(false);

  const parsed = useMemo(() => extractCitations(message.content), [message.content]);

  async function handleCopy(): Promise<void> {
    await navigator.clipboard.writeText(parsed.body);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  }

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[92%] rounded-2xl border px-4 py-3 text-sm leading-6 shadow-sm",
          isUser ? "rounded-br-md border-transparent bg-[var(--accent)] text-white" : "rounded-bl-md border-[var(--border)] bg-[var(--surface)] text-[var(--text)]",
          isSystem ? "bg-[var(--surface-2)] text-[var(--muted)]" : "",
        )}
      >
        <MarkdownContent content={parsed.body} />

        {!isUser ? (
          <div className="mt-3 flex items-center justify-between gap-3">
            <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
              {message.role} · {new Date(message.timestamp).toLocaleString()}
            </p>
            <Button variant="outline" size="sm" type="button" className="h-8 rounded-full px-3" onClick={() => void handleCopy()}>
              {copied ? <Check className="mr-2 h-4 w-4" /> : <Copy className="mr-2 h-4 w-4" />}
              {copied ? "Copied" : "Copy"}
            </Button>
          </div>
        ) : (
          <p className="mt-2 text-[11px] uppercase tracking-[0.18em] text-white/70">
            {new Date(message.timestamp).toLocaleString()}
          </p>
        )}

        {parsed.citations.length > 0 ? (
          <div className="mt-3 rounded-xl border border-[var(--border)] bg-[var(--surface-2)] p-3">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--muted)]">Citations</p>
            <ul className="mt-2 space-y-1 text-sm text-[var(--text)]">
              {parsed.citations.map((citation) => (
                <li key={citation}>{citation}</li>
              ))}
            </ul>
          </div>
        ) : null}
      </div>
    </div>
  );
}
