import { AppLogo } from "./AppLogo";
import { Spinner } from "@/components/ui/Spinner";

export function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--bg)] px-6">
      <div className="flex flex-col items-center gap-4 text-center">
        <AppLogo compact />
        <Spinner label="Loading IM Copilot..." />
      </div>
    </div>
  );
}
