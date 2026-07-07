import { type PointerEvent as ReactPointerEvent, type ReactNode, useEffect, useMemo, useRef, useState } from "react";

import { useAssistant } from "@/hooks/useAssistant";
import {
  getAssistantPanelWidth,
  getAssistantSidebarOpen,
  saveAssistantPanelWidth,
  saveAssistantSidebarOpen,
} from "@/services/storage/localStorage";
import { type AssistantMode } from "@/types";

const MIN_PANEL_WIDTH = 360;
const MAX_PANEL_WIDTH = 640;
const DEFAULT_PANEL_WIDTH = 440;

interface AssistantLayoutManagerProps {
  workspace: "guest" | "dashboard";
  onCreateConversation: () => Promise<void>;
  onCloseGuest: () => void;
  children: (layout: AssistantLayoutState) => ReactNode;
}

export interface AssistantLayoutState {
  mode: AssistantMode;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  panelWidth: number;
  sidebarOpen: boolean;
  openAssistant: () => void;
  collapseAssistant: () => void;
  fullscreenAssistant: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (nextValue: boolean) => void;
  startResize: (event: ReactPointerEvent<HTMLDivElement>) => void;
}

function getViewportState(width: number): Pick<AssistantLayoutState, "isMobile" | "isTablet" | "isDesktop"> {
  return {
    isMobile: width < 768,
    isTablet: width >= 768 && width < 1280,
    isDesktop: width >= 1280,
  };
}

function getResponsiveOpenMode(width: number): Exclude<AssistantMode, "CLOSED"> {
  if (width < 768) {
    return "FULLSCREEN";
  }
  return "DOCKED";
}

export function AssistantLayoutManager({
  workspace,
  onCreateConversation,
  onCloseGuest,
  children,
}: AssistantLayoutManagerProps) {
  const { mode, setMode } = useAssistant();
  const [viewportWidth, setViewportWidth] = useState<number>(() => {
    if (typeof window === "undefined") {
      return 1280;
    }
    return window.innerWidth;
  });
  const [panelWidth, setPanelWidthState] = useState<number>(() => getAssistantPanelWidth() ?? DEFAULT_PANEL_WIDTH);
  const [sidebarOpen, setSidebarOpenState] = useState<boolean>(() => getAssistantSidebarOpen() ?? false);
  const resizeStateRef = useRef<{ startX: number; startWidth: number } | null>(null);

  const viewport = useMemo(() => getViewportState(viewportWidth), [viewportWidth]);
  const preferredOpenMode = useMemo(() => getResponsiveOpenMode(viewportWidth), [viewportWidth]);

  useEffect(() => {
    function handleResize(): void {
      setViewportWidth(window.innerWidth);
    }

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => window.removeEventListener("resize", handleResize);
  }, []);

  useEffect(() => {
    saveAssistantPanelWidth(panelWidth);
  }, [panelWidth]);

  useEffect(() => {
    saveAssistantSidebarOpen(sidebarOpen);
  }, [sidebarOpen]);

  useEffect(() => {
    if (workspace === "guest" && mode !== "FULLSCREEN") {
      setMode("FULLSCREEN");
      return;
    }
  }, [mode, setMode, viewportWidth, workspace]);

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent): void {
      const isShortcutModifier = event.ctrlKey || event.metaKey;
      const isToggleShortcut = isShortcutModifier && event.shiftKey && event.key.toLowerCase() === "c";
      const isNewConversationShortcut = isShortcutModifier && event.key.toLowerCase() === "n";
      const isEscape = event.key === "Escape";

      if (!isToggleShortcut && !isNewConversationShortcut && !isEscape) {
        return;
      }

      if (isToggleShortcut) {
        event.preventDefault();
        if (workspace === "guest") {
          onCloseGuest();
          return;
        }

        if (mode === "DOCKED" || mode === "FULLSCREEN") {
          setMode("CLOSED");
        } else {
          setMode(getResponsiveOpenMode(viewportWidth));
        }
      }

      if (isNewConversationShortcut) {
        event.preventDefault();
        if (workspace === "dashboard" && mode === "CLOSED") {
          setMode(getResponsiveOpenMode(viewportWidth));
        }
        void onCreateConversation().catch(() => {});
      }

      if (isEscape) {
        event.preventDefault();
        if (workspace === "guest") {
          onCloseGuest();
        } else if (mode === "DOCKED" || mode === "FULLSCREEN") {
          setMode("CLOSED");
        }
      }
    }

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mode, onCloseGuest, onCreateConversation, setMode, viewportWidth, workspace]);

  return children({
    mode,
    isMobile: viewport.isMobile,
    isTablet: viewport.isTablet,
    isDesktop: viewport.isDesktop,
    panelWidth,
    sidebarOpen,
    openAssistant: () => setMode(preferredOpenMode),
    collapseAssistant: () => setMode("DOCKED"),
    fullscreenAssistant: () => setMode("FULLSCREEN"),
    toggleSidebar: () => setSidebarOpenState((current) => !current),
    setSidebarOpen: (nextValue: boolean) => setSidebarOpenState(nextValue),
    startResize: (event: ReactPointerEvent<HTMLDivElement>) => {
      if (mode !== "DOCKED") {
        return;
      }

      event.preventDefault();
      resizeStateRef.current = { startX: event.clientX, startWidth: panelWidth };

      const handleMove = (moveEvent: PointerEvent) => {
        if (!resizeStateRef.current) {
          return;
        }

        const delta = resizeStateRef.current.startX - moveEvent.clientX;
        const nextWidth = resizeStateRef.current.startWidth + delta;
        setPanelWidthState(Math.max(MIN_PANEL_WIDTH, Math.min(MAX_PANEL_WIDTH, nextWidth)));
      };

      const handleUp = () => {
        resizeStateRef.current = null;
        window.removeEventListener("pointermove", handleMove);
        window.removeEventListener("pointerup", handleUp);
      };

      window.addEventListener("pointermove", handleMove);
      window.addEventListener("pointerup", handleUp);
    },
  });
}
