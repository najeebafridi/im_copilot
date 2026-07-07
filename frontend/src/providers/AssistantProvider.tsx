import { createContext, type PropsWithChildren, useContext, useState } from "react";

import { getAssistantMode, saveAssistantMode } from "@/services/storage/localStorage";
import { type AssistantContextValue, type AssistantMode } from "@/types";

const DEFAULT_MODE: AssistantMode = "CLOSED";

const AssistantContext = createContext<AssistantContextValue | undefined>(undefined);

export function AssistantProvider({ children }: PropsWithChildren) {
  const [mode, setModeState] = useState<AssistantMode>(() => getAssistantMode() ?? DEFAULT_MODE);
  const [draftMessage, setDraftMessage] = useState("");

  function setMode(nextMode: AssistantMode): void {
    setModeState(nextMode);
    saveAssistantMode(nextMode);
  }

  return <AssistantContext.Provider value={{ mode, setMode, draftMessage, setDraftMessage }}>{children}</AssistantContext.Provider>;
}

export function useAssistantContext(): AssistantContextValue {
  const context = useContext(AssistantContext);
  if (!context) {
    throw new Error("useAssistantContext must be used within AssistantProvider");
  }
  return context;
}
