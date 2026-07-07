import { APP_ENV } from "./env";

export const APP_CONSTANTS = {
  appName: APP_ENV.appName,
  appVersion: APP_ENV.appVersion,
  maxChatTitleLength: 60,
  defaultPageSize: 10,
  storageKeys: {
    token: "im-copilot-token",
    user: "im-copilot-user",
    assistantMode: "im-copilot-assistant-mode",
  },
  featureFlags: {
    enableDebug: APP_ENV.enableDebug,
  },
} as const;
