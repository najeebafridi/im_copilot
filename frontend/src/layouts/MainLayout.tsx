import { type PropsWithChildren } from "react";
import { Outlet, useNavigate } from "react-router-dom";

import { AppLogo } from "@/components/common/AppLogo";
import { PageContainer } from "@/components/common/PageContainer";
import { ProfileMenu } from "@/components/common/ProfileMenu";
import { APP_ROUTES } from "@/config/routes";
import { useAuth } from "@/hooks/useAuth";
import { DashboardHeader } from "@/features/dashboard/DashboardHeader";

export function MainLayout({ children }: PropsWithChildren) {
  const auth = useAuth();
  const navigate = useNavigate();

  async function handleLogout(): Promise<void> {
    await auth.logout();
    navigate(APP_ROUTES.landing, { replace: true });
  }

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)]">
      <header>
        {auth.isAuthenticated && auth.user ? (
          <DashboardHeader
            title="Dashboard"
            onScrollSchedule={() => window.document.getElementById("schedule-section")?.scrollIntoView({ behavior: "smooth", block: "start" })}
            onScrollNotifications={() => window.document.getElementById("notifications-section")?.scrollIntoView({ behavior: "smooth", block: "start" })}
          />
        ) : (
          <div className="border-b border-[var(--border)] bg-[var(--surface)]/90 backdrop-blur">
            <PageContainer>
              <div className="flex items-center justify-between gap-4">
                <AppLogo compact />
                {auth.user ? <ProfileMenu user={auth.user} onLogout={() => void handleLogout()} onSettings={() => {}} /> : null}
              </div>
            </PageContainer>
          </div>
        )}
      </header>

      <div className="mx-auto min-h-[calc(100vh-9rem)] w-full max-w-7xl px-5 py-6">
        <main className="min-w-0">{children ?? <Outlet />}</main>
      </div>

      {!auth.isAuthenticated ? (
        <footer className="border-t border-[var(--border)] bg-[var(--surface)]/80">
          <PageContainer>
            <p className="text-sm text-[var(--muted)]">IM Copilot frontend shell for Phase F2B.</p>
          </PageContainer>
        </footer>
      ) : null}
    </div>
  );
}
