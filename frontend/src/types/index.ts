export type ThemeMode = "light" | "dark" | "system";
export type AuthRole = "student" | "admin";
export type StorageMode = "localStorage" | "sessionStorage";
export type LoginMode = "student" | "admin";
export type AssistantMode = "CLOSED" | "DOCKED" | "FULLSCREEN";
export type ConversationType = "GENERAL" | "ACADEMIC" | "POLICY" | "ADMIN";
export type ConversationStatus = "ACTIVE" | "LOADING" | "ERROR" | "EXPIRED";

export interface AuthLoginRequest {
  identifier: string;
  password: string;
  rememberMe: boolean;
  mode: LoginMode;
}

export interface AuthSession {
  token: string;
  user: UserProfile;
}

export interface UserProfile {
  id: string;
  name: string;
  role: AuthRole;
}

export interface AuthContextValue {
  isAuthenticated: boolean;
  user: UserProfile | null;
  loading: boolean;
  login: (request: AuthLoginRequest) => Promise<UserProfile>;
  restoreSession: () => Promise<void>;
  logout: () => Promise<void>;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export interface AssistantContext {
  page: string;
  widget: string;
  source: string;
}

export interface ConversationMessage {
  message_id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

export interface ConversationSummary {
  conversation_id: string;
  owner_id: string;
  owner_type: string;
  title: string;
  conversation_type: ConversationType;
  status: ConversationStatus;
  created_at: string;
  last_activity: string;
  message_count: number;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ConversationMessage[];
}

export interface ConversationCreateResponse {
  conversation_id: string;
  title: string;
  type: ConversationType;
  status: ConversationStatus;
}

export interface ConversationSendResponse {
  conversation: ConversationDetail;
  assistant_message: ConversationMessage;
}

export interface ConversationDeleteResponse {
  deleted: boolean;
  conversation_id: string;
}

export interface ConversationStatusResponse {
  memory_enabled: boolean;
  ttl_hours: number;
  conversation_count: number;
  memory_usage_estimate: number;
}

export interface AssistantContextValue {
  mode: AssistantMode;
  setMode: (mode: AssistantMode) => void;
  draftMessage: string;
  setDraftMessage: (draftMessage: string) => void;
}

export interface ConversationContextValue {
  conversations: ConversationSummary[];
  currentConversation: ConversationDetail | null;
  currentConversationId: string | null;
  currentAssistantContext: AssistantContext | null;
  loading: boolean;
  isSending: boolean;
  error: string | null;
  status: ConversationStatusResponse | null;
  createConversation: () => Promise<ConversationDetail>;
  selectConversation: (conversationId: string) => Promise<void>;
  sendMessage: (message: string) => Promise<void>;
  deleteConversation: (conversationId: string) => Promise<void>;
  refreshConversations: () => Promise<void>;
  setAssistantContext: (context: AssistantContext | null) => void;
}

export interface ChatContextValue {
  messages: ChatMessage[];
  currentConversationId: string | null;
  isSending: boolean;
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
}

export interface ThemeContextValue {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
}
