import logo from "@/assets/images/logo.png";
import { THEME } from "@/config/theme";

interface AppLogoProps {
  compact?: boolean;
  tone?: "light" | "dark";
}

export function AppLogo({ compact = false, tone = "dark" }: AppLogoProps) {
  const titleColor = tone === "light" ? "#FFFFFF" : THEME.colors.primary;
  const subtitleColor = tone === "light" ? "rgba(255, 255, 255, 0.72)" : THEME.colors.mutedText;

  return (
    <div className="flex items-center gap-3">
      <img src={logo} alt="IM Copilot logo" className={compact ? "h-10 w-10 rounded-xl object-cover" : "h-12 w-12 rounded-2xl object-cover"} />
      <div className="space-y-1">
        <div className="text-2xl font-semibold tracking-tight" style={{ color: titleColor }}>
          IM Copilot
        </div>
        {!compact ? (
          <p className="text-sm" style={{ color: subtitleColor }}>
            Intelligent Academic Assistant
          </p>
        ) : null}
      </div>
    </div>
  );
}
