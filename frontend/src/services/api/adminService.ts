import { apiClient } from "./apiClient";

export async function getAdminData(): Promise<unknown> {
  const response = await apiClient.get("/future/admin");
  return response.data;
}
