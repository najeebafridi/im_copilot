import { isAxiosError } from "axios";

import { apiClient } from "./apiClient";
import {
  type AssistantContext,
  type ConversationCreateResponse,
  type ConversationDeleteResponse,
  type ConversationDetail,
  type ConversationMessage,
  type ConversationSendResponse,
  type ConversationStatusResponse,
  type ConversationSummary,
} from "@/types";

function normalizeConversationError(error: unknown): Error {
  if (isAxiosError(error)) {
    if (!error.response) {
      return new Error("Cannot reach the backend server. Start the backend on port 8000.");
    }

    const detail = error.response.data;
    if (typeof detail === "object" && detail !== null && "detail" in detail && typeof detail.detail === "string") {
      return new Error(detail.detail);
    }
    if (typeof detail === "string") {
      return new Error(detail);
    }
  }

  return new Error("Conversation request failed.");
}

function buildContextBody(assistantContext?: AssistantContext | null): { assistant_context?: AssistantContext } {
  return assistantContext ? { assistant_context: assistantContext } : {};
}

export async function createConversation(
  assistantContext?: AssistantContext | null,
): Promise<ConversationCreateResponse> {
  try {
    const response = await apiClient.post<ConversationCreateResponse>(
      "/api/v1/chat/new",
      buildContextBody(assistantContext),
    );
    return response.data;
  } catch (error) {
    throw normalizeConversationError(error);
  }
}

export async function listConversations(): Promise<ConversationSummary[]> {
  try {
    const response = await apiClient.get<{ conversations: ConversationSummary[] }>("/api/v1/chat/list");
    return response.data.conversations;
  } catch (error) {
    throw normalizeConversationError(error);
  }
}

export async function getConversation(conversationId: string): Promise<ConversationDetail> {
  try {
    const response = await apiClient.get<ConversationDetail>(`/api/v1/chat/${conversationId}`);
    return response.data;
  } catch (error) {
    throw normalizeConversationError(error);
  }
}

export async function sendMessage(
  conversationId: string,
  message: string,
  assistantContext?: AssistantContext | null,
): Promise<ConversationSendResponse> {
  try {
    const response = await apiClient.post<ConversationSendResponse>(
      `/api/v1/chat/${conversationId}/message`,
      {
        message,
        ...buildContextBody(assistantContext),
      },
    );
    return response.data;
  } catch (error) {
    throw normalizeConversationError(error);
  }
}

export async function deleteConversation(conversationId: string): Promise<ConversationDeleteResponse> {
  try {
    const response = await apiClient.delete<ConversationDeleteResponse>(`/api/v1/chat/${conversationId}`);
    return response.data;
  } catch (error) {
    throw normalizeConversationError(error);
  }
}

export async function getConversationStatus(): Promise<ConversationStatusResponse> {
  try {
    const response = await apiClient.get<ConversationStatusResponse>("/api/v1/chat/status");
    return response.data;
  } catch (error) {
    throw normalizeConversationError(error);
  }
}

export type { ConversationMessage };
