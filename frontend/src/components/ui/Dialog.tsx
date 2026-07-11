import { useEffect, type PropsWithChildren } from "react";
import { X } from "lucide-react";

import { Button } from "./Button";

interface DialogProps extends PropsWithChildren {
  open: boolean;
  title: string;
  onClose: () => void;
}

export function Dialog({ open, title, onClose, children }: DialogProps) {
  useEffect(() => {
    function handleEscape(event: KeyboardEvent): void {
      if (event.key === "Escape") {
        onClose();
      }
    }

    if (!open) {
      return;
    }

    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 backdrop-blur-[2px]"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="w-full max-w-lg rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-2xl"
      >
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--muted)]">About</p>
            <h2 className="mt-1 text-2xl font-semibold text-[var(--text)]">{title}</h2>
          </div>
          <Button variant="outline" type="button" className="h-9 w-9 rounded-full p-0" onClick={onClose} aria-label="Close dialog">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="mt-5">{children}</div>
      </div>
    </div>
  );
}
