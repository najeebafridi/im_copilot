export interface AppEnv {
  apiBaseUrl: string;
  appName: string;
  appVersion: string;
  apiTimeoutMs: number;
  enableDebug: boolean;
  demoMode: boolean;
}

function parseBoolean(value: string | undefined, fallback: boolean): boolean {
  if (value === undefined) {
    return fallback;
  }
  return value.toLowerCase() === "true";
}

function parseNumber(value: string | undefined, fallback: number): number {
  if (value === undefined || value.trim() === "") {
    return fallback;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

const env = import.meta.env;

export const APP_ENV: AppEnv = {
  apiBaseUrl: env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000",
  appName: env.VITE_APP_NAME ?? "IM Copilot",
  appVersion: env.VITE_APP_VERSION ?? "1.0.0",
  apiTimeoutMs: parseNumber(env.VITE_API_TIMEOUT_MS, 15000),
  enableDebug: parseBoolean(env.VITE_ENABLE_DEBUG, false),
  demoMode: parseBoolean(env.VITE_DEMO_MODE, false),
};
