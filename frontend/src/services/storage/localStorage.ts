import { APP_CONSTANTS } from "@/config/constants";
import { type AssistantMode, type StorageMode, type UserProfile } from "@/types";

const TOKEN_KEY = APP_CONSTANTS.storageKeys.token;
const USER_KEY = APP_CONSTANTS.storageKeys.user;
const ASSISTANT_MODE_KEY = APP_CONSTANTS.storageKeys.assistantMode;
const THEME_MODE_KEY = "im-copilot-theme-mode";
const ASSISTANT_PANEL_WIDTH_KEY = "im-copilot-assistant-panel-width";
const ASSISTANT_SIDEBAR_OPEN_KEY = "im-copilot-assistant-sidebar-open";
const SELECTED_CONVERSATION_KEY = "im-copilot-selected-conversation";

function isBrowser(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function getStorage(mode: StorageMode): Storage {
  if (!isBrowser()) {
    return {
      length: 0,
      clear: () => {},
      getItem: () => null,
      key: () => null,
      removeItem: () => {},
      setItem: () => {},
    } as Storage;
  }
  return mode === "localStorage" ? window.localStorage : window.sessionStorage;
}

export function saveToken(token: string, mode: StorageMode = "localStorage"): void {
  getStorage(mode).setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  if (!isBrowser()) {
    return null;
  }
  return window.localStorage.getItem(TOKEN_KEY) ?? window.sessionStorage.getItem(TOKEN_KEY);
}

export function getTokenStorageMode(): StorageMode | null {
  if (!isBrowser()) {
    return null;
  }
  if (window.localStorage.getItem(TOKEN_KEY)) {
    return "localStorage";
  }
  if (window.sessionStorage.getItem(TOKEN_KEY)) {
    return "sessionStorage";
  }
  return null;
}

export function removeToken(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
}

export function saveUser(user: UserProfile, mode: StorageMode = "localStorage"): void {
  getStorage(mode).setItem(USER_KEY, JSON.stringify(user));
}

export function getUser(): UserProfile | null {
  if (!isBrowser()) {
    return null;
  }

  const stored = window.localStorage.getItem(USER_KEY) ?? window.sessionStorage.getItem(USER_KEY);
  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored) as UserProfile;
  } catch {
    return null;
  }
}

export function clear(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(TOKEN_KEY);
  window.localStorage.removeItem(USER_KEY);
  window.sessionStorage.removeItem(TOKEN_KEY);
  window.sessionStorage.removeItem(USER_KEY);
  window.localStorage.removeItem(ASSISTANT_PANEL_WIDTH_KEY);
  window.localStorage.removeItem(ASSISTANT_SIDEBAR_OPEN_KEY);
  window.localStorage.removeItem(SELECTED_CONVERSATION_KEY);
}

export function saveAssistantMode(mode: AssistantMode): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(ASSISTANT_MODE_KEY, mode);
}

export function getAssistantMode(): AssistantMode | null {
  if (!isBrowser()) {
    return null;
  }

  const stored = window.localStorage.getItem(ASSISTANT_MODE_KEY);
  return stored === "CLOSED" || stored === "DOCKED" || stored === "FULLSCREEN" ? stored : null;
}

export function removeAssistantMode(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(ASSISTANT_MODE_KEY);
}

export function saveThemeMode(theme: "light" | "dark" | "system"): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(THEME_MODE_KEY, theme);
}

export function getThemeMode(): "light" | "dark" | "system" | null {
  if (!isBrowser()) {
    return null;
  }

  const stored = window.localStorage.getItem(THEME_MODE_KEY);
  return stored === "light" || stored === "dark" || stored === "system" ? stored : null;
}

export function removeThemeMode(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(THEME_MODE_KEY);
}

export function saveAssistantPanelWidth(width: number): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(ASSISTANT_PANEL_WIDTH_KEY, String(Math.round(width)));
}

export function getAssistantPanelWidth(): number | null {
  if (!isBrowser()) {
    return null;
  }

  const stored = window.localStorage.getItem(ASSISTANT_PANEL_WIDTH_KEY);
  if (!stored) {
    return null;
  }

  const parsed = Number(stored);
  return Number.isFinite(parsed) ? parsed : null;
}

export function removeAssistantPanelWidth(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(ASSISTANT_PANEL_WIDTH_KEY);
}

export function saveAssistantSidebarOpen(isOpen: boolean): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(ASSISTANT_SIDEBAR_OPEN_KEY, String(isOpen));
}

export function getAssistantSidebarOpen(): boolean | null {
  if (!isBrowser()) {
    return null;
  }

  const stored = window.localStorage.getItem(ASSISTANT_SIDEBAR_OPEN_KEY);
  if (stored === null) {
    return null;
  }

  return stored === "true";
}

export function removeAssistantSidebarOpen(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(ASSISTANT_SIDEBAR_OPEN_KEY);
}

export function saveSelectedConversationId(conversationId: string): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.setItem(SELECTED_CONVERSATION_KEY, conversationId);
}

export function getSelectedConversationId(): string | null {
  if (!isBrowser()) {
    return null;
  }
  return window.localStorage.getItem(SELECTED_CONVERSATION_KEY);
}

export function removeSelectedConversationId(): void {
  if (!isBrowser()) {
    return;
  }
  window.localStorage.removeItem(SELECTED_CONVERSATION_KEY);
}
