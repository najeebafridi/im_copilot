import { createContext, type PropsWithChildren, useContext, useEffect, useState } from "react";
import { useLocation } from "react-router-dom";

import { useAuthContext } from "@/providers/AuthProvider";
import {
  createConversation as createConversationRequest,
  deleteConversation as deleteConversationRequest,
  getConversation as getConversationRequest,
  getConversationStatus,
  listConversations as listConversationsRequest,
  sendMessage as sendMessageRequest,
} from "@/services/api/conversationService";
import {
  type AssistantContext,
  type ConversationContextValue,
  type ConversationDetail,
  type ConversationSummary,
} from "@/types";
import {
  getSelectedConversationId,
  removeSelectedConversationId,
  saveSelectedConversationId,
} from "@/services/storage/localStorage";

const ConversationContext = createContext<ConversationContextValue | undefined>(undefined);

function buildDefaultAssistantContext(page: string): AssistantContext {
  return {
    page,
    widget: "assistant",
    source: "frontend",
  };
}

function summarizeToDetail(summary: ConversationSummary): ConversationDetail {
  return {
    ...summary,
    messages: [],
  };
}

export function ConversationProvider({ children }: PropsWithChildren) {
  const auth = useAuthContext();
  const location = useLocation();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [currentConversation, setCurrentConversation] = useState<ConversationDetail | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [currentAssistantContext, setCurrentAssistantContext] = useState<AssistantContext | null>(
    buildDefaultAssistantContext(location.pathname),
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<ConversationContextValue["status"]>(null);

  useEffect(() => {
    setCurrentAssistantContext((current) => {
      const base = current ?? buildDefaultAssistantContext(location.pathname);
      return { ...base, page: location.pathname };
    });
  }, [location.pathname]);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap(): Promise<void> {
      if (auth.loading) {
        setLoading(true);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const [statusPayload, conversationList] = await Promise.all([
          getConversationStatus(),
          listConversationsRequest(),
        ]);

        if (cancelled) {
          return;
        }

        setStatus(statusPayload);
        setConversations(conversationList);

        if (conversationList.length > 0) {
          const preferredConversationId = getSelectedConversationId();
          const selectedConversation =
            conversationList.find((conversation) => conversation.conversation_id === preferredConversationId) ??
            conversationList[0];
          const detail = await getConversationRequest(selectedConversation.conversation_id);
          if (!cancelled) {
            setCurrentConversation(detail);
            setCurrentConversationId(detail.conversation_id);
            saveSelectedConversationId(detail.conversation_id);
          }
        } else {
          setCurrentConversation(null);
          setCurrentConversationId(null);
          removeSelectedConversationId();
        }
      } catch (bootstrapError) {
        if (!cancelled) {
          setError(bootstrapError instanceof Error ? bootstrapError.message : "Conversation loading failed.");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, [auth.loading, auth.isAuthenticated, auth.user?.id]);

  async function refreshConversations(preferredConversationId: string | null = currentConversationId): Promise<void> {
    try {
      const [statusPayload, conversationList] = await Promise.all([
        getConversationStatus(),
        listConversationsRequest(),
      ]);

      setStatus(statusPayload);
      setConversations(conversationList);

      if (preferredConversationId) {
        const updatedConversation = conversationList.find(
          (conversation) => conversation.conversation_id === preferredConversationId,
        );
        if (updatedConversation) {
          try {
            setCurrentConversation(await getConversationRequest(preferredConversationId));
            setCurrentConversationId(preferredConversationId);
            saveSelectedConversationId(preferredConversationId);
          } catch {
            setCurrentConversation(summarizeToDetail(updatedConversation));
            setCurrentConversationId(preferredConversationId);
            saveSelectedConversationId(preferredConversationId);
          }
        } else {
          setCurrentConversation(null);
          if (preferredConversationId === currentConversationId) {
            setCurrentConversationId(null);
          }
          removeSelectedConversationId();
        }
      }
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "Conversation refresh failed.");
    }
  }

  async function createConversation(): Promise<ConversationDetail> {
    setError(null);
    try {
      const created = await createConversationRequest(currentAssistantContext);
      const now = new Date().toISOString();
      const detail = {
        conversation_id: created.conversation_id,
        owner_id: auth.user?.id ?? "guest",
        owner_type: auth.isAuthenticated ? auth.user?.role ?? "guest" : "guest",
        title: created.title,
        conversation_type: created.type,
        status: created.status,
        created_at: now,
        last_activity: now,
        message_count: 0,
        messages: [],
      } satisfies ConversationDetail;

      setConversations((current) => [detail, ...current.filter((item) => item.conversation_id !== detail.conversation_id)]);
      setCurrentConversation(detail);
      setCurrentConversationId(detail.conversation_id);
      saveSelectedConversationId(detail.conversation_id);
      await refreshConversations(detail.conversation_id);
      return detail;
    } catch (createError) {
      setError(createError instanceof Error ? createError.message : "Conversation creation failed.");
      throw createError;
    }
  }

  async function selectConversation(conversationId: string): Promise<void> {
    setError(null);
    try {
      const detail = await getConversationRequest(conversationId);
      setCurrentConversation(detail);
      setCurrentConversationId(conversationId);
      saveSelectedConversationId(conversationId);
    } catch (selectError) {
      setError(selectError instanceof Error ? selectError.message : "Conversation selection failed.");
      throw selectError;
    }
  }

  async function sendMessage(message: string): Promise<void> {
    setError(null);
    setIsSending(true);
    try {
      let conversationId = currentConversationId;
      if (!conversationId) {
        const createdConversation = await createConversation();
        conversationId = createdConversation.conversation_id;
      }

      const response = await sendMessageRequest(conversationId, message, currentAssistantContext);
      setCurrentConversation(response.conversation);
      setCurrentConversationId(response.conversation.conversation_id);
      await refreshConversations(response.conversation.conversation_id);
    } catch (sendError) {
      setError(sendError instanceof Error ? sendError.message : "Conversation send failed.");
      throw sendError;
    } finally {
      setIsSending(false);
    }
  }

  async function deleteConversation(conversationId: string): Promise<void> {
    setError(null);
    try {
      await deleteConversationRequest(conversationId);
      const remainingConversations = conversations.filter((conversation) => conversation.conversation_id !== conversationId);
      setConversations(remainingConversations);

      if (currentConversationId === conversationId) {
        setCurrentConversation(null);
        setCurrentConversationId(null);
        removeSelectedConversationId();
        if (remainingConversations.length > 0) {
          await selectConversation(remainingConversations[0].conversation_id);
        }
      }
    } catch (deleteError) {
      setError(deleteError instanceof Error ? deleteError.message : "Conversation deletion failed.");
      throw deleteError;
    }
  }

  const value: ConversationContextValue = {
    conversations,
    currentConversation,
    currentConversationId,
    currentAssistantContext,
    loading,
    isSending,
    error,
    status,
    createConversation,
    selectConversation,
    sendMessage,
    deleteConversation,
    refreshConversations,
    setAssistantContext: setCurrentAssistantContext,
  };

  return <ConversationContext.Provider value={value}>{children}</ConversationContext.Provider>;
}

export function useConversationContext(): ConversationContextValue {
  const context = useContext(ConversationContext);
  if (!context) {
    throw new Error("useConversationContext must be used within ConversationProvider");
  }
  return context;
}
