import { APP_ROUTES } from "@/config/routes";
import { type AuthRole, type UserProfile } from "@/types";

import { PERMISSIONS, type Permission, hasPermission } from "./permissions";

export function getHomePathForRole(role: AuthRole | null): string {
  if (role === "admin") {
    return "/admin";
  }
  if (role === "student") {
    return "/student";
  }
  return APP_ROUTES.landing;
}

export function canAccessPermission(user: UserProfile | null, permission: Permission): boolean {
  return hasPermission(user?.role ?? null, permission);
}

export { PERMISSIONS, hasPermission };
