import { useNavigate } from "react-router-dom";

import { AppLogo } from "@/components/common/AppLogo";
import { PageContainer } from "@/components/common/PageContainer";
import { PageCard } from "@/components/common/PageCard";
import { Button } from "@/components/ui/Button";
import { APP_ROUTES } from "@/config/routes";

export function NotFound() {
  const navigate = useNavigate();

  return (
    <PageContainer>
      <div className="flex min-h-[70vh] items-center justify-center">
        <PageCard className="w-full max-w-xl">
          <div className="space-y-6 text-center">
            <AppLogo compact />
            <div className="space-y-2">
              <p className="text-6xl font-semibold tracking-tight">404</p>
              <h1 className="text-2xl font-semibold">Page Not Found</h1>
              <p className="text-sm text-[var(--muted)]">
                The page you are looking for does not exist.
              </p>
            </div>
            <Button variant="outline" type="button" onClick={() => navigate(APP_ROUTES.landing, { replace: true })}>
              Return Home
            </Button>
          </div>
        </PageCard>
      </div>
    </PageContainer>
  );
}
