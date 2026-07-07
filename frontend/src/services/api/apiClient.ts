import axios from "axios";

import { APP_ENV } from "@/config/env";
import { getToken } from "@/services/storage/localStorage";

export const apiClient = axios.create({
  baseURL: APP_ENV.apiBaseUrl,
  timeout: APP_ENV.apiTimeoutMs,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Future auth header injection is centralized here.
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers = config.headers ?? {};
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// Placeholder for future response handling and refresh logic.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);
