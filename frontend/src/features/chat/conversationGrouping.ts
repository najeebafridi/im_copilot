import { type ConversationSummary } from "@/types";

export interface ConversationGroup {
  label: string;
  conversations: ConversationSummary[];
}

function startOfDay(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate());
}

function daysBetween(reference: Date, target: Date): number {
  const millisPerDay = 24 * 60 * 60 * 1000;
  const referenceDay = startOfDay(reference).getTime();
  const targetDay = startOfDay(target).getTime();
  return Math.floor((referenceDay - targetDay) / millisPerDay);
}

export function groupConversationsByDate(conversations: ConversationSummary[]): ConversationGroup[] {
  const sorted = [...conversations].sort(
    (left, right) => new Date(right.last_activity).getTime() - new Date(left.last_activity).getTime(),
  );

  const today: ConversationSummary[] = [];
  const yesterday: ConversationSummary[] = [];
  const previous: ConversationSummary[] = [];
  const now = new Date();

  for (const conversation of sorted) {
    const delta = daysBetween(now, new Date(conversation.last_activity));
    if (delta === 0) {
      today.push(conversation);
      continue;
    }

    if (delta === 1) {
      yesterday.push(conversation);
      continue;
    }

    previous.push(conversation);
  }

  return [
    { label: "Today", conversations: today },
    { label: "Yesterday", conversations: yesterday },
    { label: "Previous", conversations: previous },
  ].filter((group) => group.conversations.length > 0);
}

export function getConversationTypeLabel(conversationType: ConversationSummary["conversation_type"]): string {
  const labels: Record<ConversationSummary["conversation_type"], string> = {
    GENERAL: "General",
    ACADEMIC: "Academic",
    POLICY: "Policy",
    ADMIN: "Admin",
  };

  return labels[conversationType];
}
