import { useConversationContext } from "@/providers/ConversationProvider";

export function useConversation() {
  return useConversationContext();
}
