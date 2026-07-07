import { useConversationContext } from "@/providers/ConversationProvider";

export function useChat() {
  return useConversationContext();
}
