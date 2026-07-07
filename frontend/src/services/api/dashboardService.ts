import { apiClient } from "./apiClient";

export async function getDashboardData(): Promise<unknown> {
  const response = await apiClient.get("/future/dashboard");
  return response.data;
}
