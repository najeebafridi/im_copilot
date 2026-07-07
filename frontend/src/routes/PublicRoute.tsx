import { Navigate, Outlet } from "react-router-dom";

import { APP_ROUTES } from "@/config/routes";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { useAuth } from "@/hooks/useAuth";
import { getHomePathForRole } from "@/services/auth/authGuard";

export function PublicRoute() {
  const auth = useAuth();

  if (auth.loading) {
    return <LoadingScreen />;
  }

  if (auth.isAuthenticated) {
    return <Navigate to={getHomePathForRole(auth.user?.role ?? null)} replace />;
  }

  return <Outlet />;
}
