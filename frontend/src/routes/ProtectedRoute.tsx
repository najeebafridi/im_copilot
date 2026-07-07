import { Navigate, Outlet } from "react-router-dom";

import { APP_ROUTES } from "@/config/routes";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { useAuth } from "@/hooks/useAuth";

import { type Permission } from "@/services/auth/permissions";
import { hasPermission } from "@/services/auth/permissions";

interface ProtectedRouteProps {
  permission: Permission;
}

export function ProtectedRoute({ permission }: ProtectedRouteProps) {
  const auth = useAuth();

  if (auth.loading) {
    return <LoadingScreen />;
  }

  if (!auth.user || !hasPermission(auth.user.role, permission)) {
    return <Navigate to={APP_ROUTES.landing} replace />;
  }

  return <Outlet />;
}
