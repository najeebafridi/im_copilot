import { createContext, type PropsWithChildren, useEffect, useState, useContext } from "react";

import { getThemeMode, saveThemeMode } from "@/services/storage/localStorage";
import { type ThemeContextValue } from "@/types";

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined);

export function ThemeProvider({ children }: PropsWithChildren) {
  const [theme, setThemeState] = useState<"light" | "dark" | "system">(() => getThemeMode() ?? "system");

  useEffect(() => {
    const root = document.documentElement;
    const resolvedTheme =
      theme === "system" ? (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light") : theme;

    root.classList.remove("light", "dark");
    root.classList.add(resolvedTheme);
    root.style.colorScheme = resolvedTheme;
  }, [theme]);

  useEffect(() => {
    const media = window.matchMedia("(prefers-color-scheme: dark)");
    function handleChange(): void {
      if (theme === "system") {
        setThemeState("system");
      }
    }

    media.addEventListener("change", handleChange);
    return () => media.removeEventListener("change", handleChange);
  }, [theme]);

  function setTheme(nextTheme: "light" | "dark" | "system"): void {
    setThemeState(nextTheme);
    saveThemeMode(nextTheme);
  }

  return <ThemeContext.Provider value={{ theme, setTheme }}>{children}</ThemeContext.Provider>;
}

export function useThemeContext(): ThemeContextValue {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error("useThemeContext must be used within ThemeProvider");
  }
  return context;
}
