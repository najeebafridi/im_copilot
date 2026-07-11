import { type PropsWithChildren } from "react";
import { Outlet, useNavigate } from "react-router-dom";

import { AppLogo } from "@/components/common/AppLogo";
import { ProfileMenu } from "@/components/common/ProfileMenu";
import { PageContainer } from "@/components/common/PageContainer";
import { APP_ROUTES } from "@/config/routes";
import { useAuth } from "@/hooks/useAuth";

export function AdminLayout({ children }: PropsWithChildren) {
  const auth = useAuth();
  const navigate = useNavigate();

  async function handleLogout(): Promise<void> {
    await auth.logout();
    navigate(APP_ROUTES.landing, { replace: true });
  }

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <header className="border-b border-[var(--border)] bg-[var(--surface)]/90 backdrop-blur">
        <PageContainer>
          <div className="flex items-center justify-between gap-4">
            <AppLogo compact />
            {auth.isAuthenticated && auth.user ? (
              <ProfileMenu
                user={auth.user}
                onLogout={() => void handleLogout()}
                onSettings={() => {}}
              />
            ) : null}
          </div>
        </PageContainer>
      </header>

      <div className="mx-auto min-h-[calc(100vh-4rem)] w-full max-w-7xl px-5 py-6">
        <main className="min-w-0">{children ?? <Outlet />}</main>
      </div>
    </div>
  );
}
