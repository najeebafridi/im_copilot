import { useState } from "react";
import { cn } from "@/utils/cn";
import { type ConversationDetail, type ConversationSummary } from "@/types";
import { ChevronLeft, Minimize2, MoonStar, PanelLeftClose, PanelRightClose, Settings2, Square, SunMedium, X } from "lucide-react";
import { useThemeContext } from "@/providers/ThemeProvider";

import { ConversationSidebar } from "./ConversationSidebar";
import { ConversationWorkspace } from "./ConversationWorkspace";
import { type AssistantLayoutState } from "./AssistantLayoutManager";

interface AssistantPanelProps {
  workspace: "guest" | "dashboard";
  layout: AssistantLayoutState;
  conversations: ConversationSummary[];
  currentConversation: ConversationDetail | null;
  currentConversationId: string | null;
  loading: boolean;
  isSending: boolean;
  error: string | null;
  onCreateConversation: () => Promise<void>;
  onSelectConversation: (conversationId: string) => Promise<void>;
  onDeleteConversation: (conversationId: string) => Promise<void>;
  onSettings: () => void;
  onClose: () => void;
}

function modePadding(mode: AssistantLayoutState["mode"]): string {
  return mode === "DOCKED" ? "p-2" : "p-4";
}

export function AssistantPanel({
  workspace,
  layout,
  conversations,
  currentConversation,
  currentConversationId,
  loading,
  isSending,
  error,
  onCreateConversation,
  onSelectConversation,
  onDeleteConversation,
  onSettings,
  onClose,
}: AssistantPanelProps) {
  const { theme, setTheme } = useThemeContext();
  const [guestSettingsOpen, setGuestSettingsOpen] = useState(false);
  const isGuest = workspace === "guest";
  const mode = isGuest ? "FULLSCREEN" : layout.mode;
  const isDocked = mode === "DOCKED";
  const isFullscreen = mode === "FULLSCREEN";
  const showSidebar = isGuest ? true : layout.sidebarOpen;
  const panelClassName = cn(
    "fixed z-30 overflow-hidden border border-slate-200 bg-white text-slate-900 shadow-2xl transition-all duration-200",
    isDocked ? "right-0 top-0 bottom-0 rounded-l-3xl border-r-0" : "",
    isFullscreen ? "inset-0 rounded-none border-0 shadow-none" : "",
  );

  const panelStyle = isDocked
    ? {
        width: `${layout.panelWidth}px`,
        maxWidth: "calc(100vw - 3rem)",
      }
    : undefined;

  return (
    <section className={panelClassName} style={panelStyle} aria-label="IM Copilot assistant workspace">
      {isDocked ? (
        <div
          className="absolute left-0 top-0 z-20 h-full w-2 cursor-col-resize bg-transparent transition-colors hover:bg-slate-200"
          onPointerDown={layout.startResize}
          role="presentation"
          aria-hidden="true"
        />
      ) : null}

      <div className="flex h-full min-h-0 flex-col">
        <div className={cn("flex items-center justify-between border-b border-slate-200", modePadding(mode))}>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h2 className={cn("truncate font-semibold text-slate-900", isDocked ? "text-sm" : "text-lg")}>
                {currentConversation?.title ?? "IM Copilot"}
              </h2>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {isGuest ? (
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition-colors hover:bg-slate-100"
                onClick={() => setGuestSettingsOpen((current) => !current)}
                aria-label="Open settings"
                title="Settings"
              >
                <Settings2 className="h-4 w-4" />
              </button>
            ) : null}

            {!isGuest ? (
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition-colors hover:bg-slate-100"
                onClick={layout.toggleSidebar}
                aria-label={layout.sidebarOpen ? "Hide sidebar" : "Show sidebar"}
                title={layout.sidebarOpen ? "Hide sidebar" : "Show sidebar"}
              >
                {layout.sidebarOpen ? <PanelLeftClose className="h-4 w-4" /> : <PanelRightClose className="h-4 w-4" />}
              </button>
            ) : null}

            {!isGuest ? (
              <button
                type="button"
                className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition-colors hover:bg-slate-100"
                onClick={isFullscreen ? layout.collapseAssistant : layout.fullscreenAssistant}
                aria-label={isFullscreen ? "Return to docked" : "Enter fullscreen"}
                title={isFullscreen ? "Return to docked" : "Enter fullscreen"}
              >
                {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Square className="h-4 w-4" />}
              </button>
            ) : null}

            <button
              type="button"
              className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition-colors hover:bg-slate-100"
              onClick={onClose}
              aria-label={isGuest ? "Back" : "Close assistant"}
              title={isGuest ? "Back" : "Close assistant"}
            >
              {isGuest ? <ChevronLeft className="h-4 w-4" /> : <X className="h-4 w-4" />}
            </button>

          </div>
        </div>

        {isGuest && guestSettingsOpen ? (
          <div className="border-b border-slate-200 bg-slate-50 px-4 py-3">
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            >
              {theme === "dark" ? <SunMedium className="h-4 w-4" /> : <MoonStar className="h-4 w-4" />}
              {theme === "dark" ? "Switch to light" : "Switch to dark"}
            </button>
          </div>
        ) : null}

        <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
          {showSidebar ? (
            <div className={cn("min-h-0 border-r border-slate-200", isDocked ? "w-[220px]" : "w-[260px]")}>
              <ConversationSidebar
                conversations={conversations}
                currentConversationId={currentConversationId}
                loading={loading}
                error={error}
                onCreateConversation={onCreateConversation}
                onSelectConversation={onSelectConversation}
                onDeleteConversation={onDeleteConversation}
                onSettings={onSettings}
                compact={isDocked}
              />
            </div>
          ) : null}

          <div className="min-h-0 flex-1 bg-[linear-gradient(180deg,#ffffff_0%,#f8fafc_100%)]">
            <ConversationWorkspace
              conversation={currentConversation}
              loading={loading}
              isSending={isSending}
              compact={isDocked}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
