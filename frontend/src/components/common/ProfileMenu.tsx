import { useEffect, useRef, useState } from "react";
import { CircleUserRound, LogOut, MoonStar, Settings2, SunMedium, UserRound } from "lucide-react";

import { Button } from "@/components/ui/Button";
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

  const menuBg = tone === "light" ? "bg-slate-900 text-white" : "bg-white text-slate-900";
  const panelBorder = tone === "light" ? "border-white/10" : "border-slate-200";
  const hoverItemClass = tone === "light" ? "hover:bg-white/10" : "hover:bg-slate-100";
  const secondaryTextClass = tone === "light" ? "text-white/70" : "text-slate-500";

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
          <div className={cn("flex items-center gap-3 border-b px-4 py-4", tone === "light" ? "border-white/10" : "border-slate-200")}>
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-slate-100 text-slate-700">
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

      {aboutOpen ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/45 px-4">
          <div className={cn("w-full max-w-md rounded-2xl border p-6 shadow-2xl", menuBg, panelBorder)}>
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface-2)]">
                <CircleUserRound className="h-5 w-5" />
              </div>
              <div>
                <p className="text-lg font-semibold">About IM Copilot</p>
                <p className={cn("text-sm", secondaryTextClass)}>Academic assistant for a university environment.</p>
              </div>
            </div>
            <p className={cn("mt-4 text-sm leading-6", secondaryTextClass)}>
              IM Copilot combines dashboard information, student support, and a conversational assistant for academic tasks.
            </p>
            <div className="mt-6 flex justify-end">
              <Button type="button" variant="outline" onClick={() => setAboutOpen(false)}>
                Close
              </Button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
