import { useEffect } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { AppLogo } from "@/components/common/AppLogo";
import { PageCard } from "@/components/common/PageCard";
import { PageContainer } from "@/components/common/PageContainer";
import { PageHeader } from "@/components/common/PageHeader";
import { Button } from "@/components/ui/Button";
import { APP_ROUTES } from "@/config/routes";
import { useAuth } from "@/hooks/useAuth";
import { useThemeContext } from "@/providers/ThemeProvider";
import { getHomePathForRole } from "@/services/auth/authGuard";

export function Landing() {
  const auth = useAuth();
  const navigate = useNavigate();
  const { setTheme } = useThemeContext();

  useEffect(() => {
    setTheme("light");
  }, [setTheme]);

  if (auth.isAuthenticated) {
    return <Navigate to={getHomePathForRole(auth.user?.role ?? null)} replace />;
  }

  const actions = [
    {
      title: "Continue as Guest",
      description: "Open the limited-access public view without signing in.",
      badge: "G",
      label: "Open Guest View",
      onClick: () => navigate(APP_ROUTES.guest),
    },
    {
      title: "Continue as Student",
      description: "Use student credentials to access the authenticated academic area.",
      badge: "S",
      label: "Student Login",
      onClick: () => navigate(APP_ROUTES.login),
    },
    {
      title: "Continue as Administrator",
      description: "Use administrator credentials to access admin-specific pages.",
      badge: "A",
      label: "Administrator Login",
      onClick: () => navigate(APP_ROUTES.adminLogin),
    },
  ] as const;

  return (
    <PageContainer>
      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="space-y-6">
          <AppLogo />
          <PageHeader
            title="IM Copilot"
            description="An intelligent academic assistant for students and guests in a university environment."
          />
          <p className="max-w-2xl text-sm leading-6 text-[var(--muted)]">
            A polished entry experience, simple navigation, and clear access paths for every role.
          </p>
        </div>

        <PageCard>
          <div className="space-y-4">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">Choose access mode</p>
              <h2 className="mt-2 text-xl font-semibold text-[var(--text)]">Continue into the project</h2>
            </div>

            <div className="grid gap-4">
              {actions.map((item) => (
                <div
                  key={item.title}
                  className="flex flex-col gap-4 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 sm:flex-row sm:items-center sm:justify-between"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[var(--accent)] text-lg font-semibold text-white">
                      {item.badge}
                    </div>
                    <div className="space-y-1">
                      <h3 className="text-base font-semibold text-[var(--text)]">{item.title}</h3>
                      <p className="text-sm leading-6 text-[var(--muted)]">{item.description}</p>
                    </div>
                  </div>
                  <Button variant="outline" type="button" onClick={item.onClick} className="sm:min-w-[180px]">
                    {item.label}
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </PageCard>
      </div>
    </PageContainer>
  );
}
