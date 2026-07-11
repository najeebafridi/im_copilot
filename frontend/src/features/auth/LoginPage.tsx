import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Navigate, useNavigate } from "react-router-dom";

import { AppLogo } from "@/components/common/AppLogo";
import { PageCard } from "@/components/common/PageCard";
import { PageContainer } from "@/components/common/PageContainer";
import { Alert } from "@/components/ui/Alert";
import { Button } from "@/components/ui/Button";
import { Checkbox } from "@/components/ui/Checkbox";
import { Divider } from "@/components/ui/Divider";
import { Input } from "@/components/ui/Input";
import { APP_ROUTES } from "@/config/routes";
import { useAuth } from "@/hooks/useAuth";
import { useThemeContext } from "@/providers/ThemeProvider";
import { getHomePathForRole } from "@/services/auth/authGuard";
import { type LoginMode } from "@/types";

interface LoginPageProps {
  mode: LoginMode;
}

export function LoginPage({ mode }: LoginPageProps) {
  const auth = useAuth();
  const navigate = useNavigate();
  const { setTheme } = useThemeContext();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const pageTitle = mode === "student" ? "Student Login" : "Administrator Login";
  const identifierLabel = mode === "student" ? "Student ID" : "Username";
  const identifierPlaceholder = mode === "student" ? "DS001" : "admin";
  const passwordPlaceholder = mode === "student" ? "Enter your password" : "Enter administrator password";
  const pageDescription =
    mode === "student"
      ? "Sign in with your student ID to access your personal academic area."
      : "Sign in with administrator credentials to manage the academic workspace.";

  const errorMessage = useMemo(() => {
    if (!error) {
      return null;
    }

    const normalized = error.toLowerCase();
    if (normalized.includes("unauthorized")) {
      return "Invalid username or password. Please check your credentials and try again.";
    }
    if (normalized.includes("network")) {
      return "Network error. Please check your connection and try again.";
    }
    if (normalized.includes("server")) {
      return "Server unavailable. Please try again after a moment.";
    }
    return error;
  }, [error]);

  useEffect(() => {
    setTheme("light");
  }, [setTheme]);

  if (auth.isAuthenticated) {
    return <Navigate to={getHomePathForRole(auth.user?.role ?? null)} replace />;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const user = await auth.login({
        identifier,
        password,
        rememberMe,
        mode,
      });
      navigate(getHomePathForRole(user.role), { replace: true });
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : "Login failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <PageContainer>
      <div className="mx-auto grid min-h-[calc(100vh-6rem)] max-w-5xl items-center lg:grid-cols-[0.95fr_1.05fr] lg:gap-8">
        <div className="hidden space-y-6 lg:block">
          <AppLogo />
          <div className="space-y-3">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-[var(--muted)]">Secure access</p>
            <h1 className="text-4xl font-semibold tracking-tight text-[var(--text)]">{pageTitle}</h1>
            <p className="max-w-xl text-base leading-7 text-[var(--muted)]">{pageDescription}</p>
          </div>
        </div>

        <PageCard className="mx-auto w-full max-w-xl">
          <div className="space-y-6">
            <div className="space-y-2 text-center">
              <div className="lg:hidden">
                <AppLogo compact />
              </div>
              <h2 className="text-2xl font-semibold tracking-tight text-[var(--text)]">{pageTitle}</h2>
              <p className="text-sm leading-6 text-[var(--muted)]">{pageDescription}</p>
            </div>

            {errorMessage ? <Alert variant="error">{errorMessage}</Alert> : null}

            <form className="space-y-4" onSubmit={handleSubmit}>
              <Input
                id="identifier"
                name="identifier"
                label={identifierLabel}
                type="text"
                value={identifier}
                onChange={(event) => setIdentifier(event.target.value)}
                placeholder={identifierPlaceholder}
                autoComplete="username"
                disabled={submitting}
                required
              />

              <Input
                id="password"
                name="password"
                label="Password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder={passwordPlaceholder}
                autoComplete="current-password"
                disabled={submitting}
                required
              />

              <Checkbox
                label="Stay Logged In"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
                disabled={submitting}
              />

              <Button type="submit" loading={submitting} className="w-full">
                Login
              </Button>
            </form>

            <Divider />

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <Button
                variant="outline"
                type="button"
                onClick={() => navigate(APP_ROUTES.landing)}
                className="sm:w-auto"
              >
                Back to Home
              </Button>
              <p className="text-xs text-[var(--muted)]">Need help? Use the credentials provided for your role.</p>
            </div>
          </div>
        </PageCard>
      </div>
    </PageContainer>
  );
}
