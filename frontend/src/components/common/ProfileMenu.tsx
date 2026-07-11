import { useEffect, useRef, useState } from "react";
import { CircleUserRound, LogOut, MoonStar, Settings2, SunMedium, UserRound } from "lucide-react";

import { Button } from "@/components/ui/Button";
import { Dialog } from "@/components/ui/Dialog";
import { useThemeContext } from "@/providers/ThemeProvider";
import { cn } from "@/utils/cn";
import { type UserProfile } from "@/types";

interface ProfileMenuProps {
  user: UserProfile;
  onLogout: () => void;
  onSettings: () => void;
  className?: string;
  tone?: "light" | "dark";
}

export function ProfileMenu({ user, onLogout, onSettings, className, tone = "dark" }: ProfileMenuProps) {
  const [open, setOpen] = useState(false);
  const [aboutOpen, setAboutOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement | null>(null);
  const { theme, setTheme } = useThemeContext();

  useEffect(() => {
    function handleClickOutside(event: MouseEvent): void {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }

    function handleEscape(event: KeyboardEvent): void {
      if (event.key === "Escape") {
        setOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, []);

  const menuBg = tone === "light" ? "bg-[var(--surface)] text-[var(--text)]" : "bg-[var(--surface)] text-[var(--text)]";
  const panelBorder = "border-[var(--border)]";
  const hoverItemClass = "hover:bg-[var(--surface-2)]";
  const secondaryTextClass = "text-[var(--muted)]";

  return (
    <div ref={rootRef} className={cn("relative", className)}>
      <Button
        variant="outline"
        type="button"
        className="h-11 w-11 rounded-full p-0"
        onClick={() => setOpen((current) => !current)}
        aria-label="Open profile menu"
      >
        <CircleUserRound className="h-5 w-5" />
      </Button>

      {open ? (
        <div className={cn("absolute right-0 top-14 z-50 w-72 overflow-hidden rounded-2xl border shadow-xl", menuBg, panelBorder)}>
          <div className={cn("flex items-center gap-3 border-b px-4 py-4", "border-[var(--border)]")}>
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[var(--surface-2)] text-[var(--text)]">
              <UserRound className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold">{user.name}</p>
              <p className={cn("text-xs", secondaryTextClass)}>Student ID: {user.id}</p>
            </div>
          </div>

          <div className="space-y-1 p-3">
            <button
              type="button"
              className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm", hoverItemClass)}
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
              {theme === "dark" ? "Light theme" : "Dark theme"}
            </button>
            <button
              type="button"
              className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm", hoverItemClass)}
              onClick={onSettings}
            >
              <Settings2 className="h-4 w-4" />
              Quick settings
            </button>
            <button
              type="button"
              className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm", hoverItemClass)}
              onClick={onSettings}
            >
              <Settings2 className="h-4 w-4" />
              Full settings
            </button>
            <button
              type="button"
              className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm", hoverItemClass)}
              onClick={() => setAboutOpen(true)}
            >
              <UserRound className="h-4 w-4" />
              About IM Copilot
            </button>
            <button
              type="button"
              className={cn("flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm", tone === "light" ? "hover:bg-red-500/10" : "hover:bg-red-500/10")}
              onClick={onLogout}
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      ) : null}

      <Dialog open={aboutOpen} title="IM Copilot" onClose={() => setAboutOpen(false)}>
        <div className="grid gap-3 text-sm text-[var(--muted)]">
          <div className="flex items-center justify-between gap-4 rounded-xl bg-[var(--surface-2)] px-4 py-3">
            <span>Project</span>
            <span className="font-medium text-[var(--text)]">IM Copilot</span>
          </div>
          <div className="flex items-center justify-between gap-4 rounded-xl bg-[var(--surface-2)] px-4 py-3">
            <span>Version</span>
            <span className="font-medium text-[var(--text)]">1.0.0</span>
          </div>
          <div className="flex items-center justify-between gap-4 rounded-xl bg-[var(--surface-2)] px-4 py-3">
            <span>Developers</span>
            <span className="font-medium text-[var(--text)]">Najeeb Ullah, Madiha Shahab, Muneeze Malik</span>
          </div>
          <div className="flex items-center justify-between gap-4 rounded-xl bg-[var(--surface-2)] px-4 py-3">
            <span>Department</span>
            <span className="font-medium text-[var(--text)]">Data Science</span>
          </div>
          <div className="flex items-center justify-between gap-4 rounded-xl bg-[var(--surface-2)] px-4 py-3">
            <span>University</span>
            <span className="font-medium text-[var(--text)]">IM|Sciences</span>
          </div>
          <div className="flex items-center justify-between gap-4 rounded-xl bg-[var(--surface-2)] px-4 py-3">
            <span>Supervisor</span>
            <span className="font-medium text-[var(--text)]">Prof. Dr. Awais Adnan</span>
          </div>
        </div>
      </Dialog>
    </div>
  );
}
