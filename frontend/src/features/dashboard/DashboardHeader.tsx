import { Bell, CalendarDays } from "lucide-react";

import { AppLogo } from "@/components/common/AppLogo";
import { ProfileMenu } from "@/components/common/ProfileMenu";
import { useAuth } from "@/hooks/useAuth";

interface DashboardHeaderProps {
  title: string;
  onScrollSchedule: () => void;
  onScrollNotifications: () => void;
}

export function DashboardHeader({ title, onScrollSchedule, onScrollNotifications }: DashboardHeaderProps) {
  const auth = useAuth();

  return (
    <header className="flex items-center justify-between gap-4 border-b border-[var(--border)] bg-[var(--surface)] px-5 py-4">
      <AppLogo compact />

      <div className="flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <p className="text-base font-semibold text-[var(--text)]">{title}</p>
          <p className="text-xs text-[var(--muted)]">Student dashboard</p>
        </div>

        <button
          type="button"
          className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface-2)] text-[var(--text)] transition-all hover:-translate-y-[1px] hover:shadow-md"
          aria-label="Today's schedule"
          title="Today's schedule"
          onClick={onScrollSchedule}
        >
          <CalendarDays className="h-4 w-4" />
        </button>

        <button
          type="button"
          className="inline-flex h-11 w-11 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface-2)] text-[var(--text)] transition-all hover:-translate-y-[1px] hover:shadow-md"
          aria-label="Notifications"
          title="Notifications"
          onClick={onScrollNotifications}
        >
          <Bell className="h-4 w-4" />
        </button>

        {auth.user ? <ProfileMenu user={auth.user} onLogout={() => void auth.logout()} onSettings={() => {}} /> : null}
      </div>
    </header>
  );
}
