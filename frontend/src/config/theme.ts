export const THEME = {
  colors: {
    primary: "var(--accent)",
    secondary: "var(--accent-2)",
    background: "var(--bg)",
    surface: "var(--surface)",
    border: "var(--border)",
    text: "var(--text)",
    mutedText: "var(--muted)",
    success: "#15803d",
    warning: "#d97706",
    error: "#dc2626",
  },
  radius: {
    sm: "10px",
    md: "14px",
    lg: "18px",
  },
  shadow: {
    card: "0 8px 24px rgba(16, 36, 59, 0.08)",
  },
  spacing: {
    pageX: "1.25rem",
    pageY: "1.5rem",
  },
} as const;
