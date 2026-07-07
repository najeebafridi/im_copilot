import { useNavigate } from "react-router-dom";

import { APP_ROUTES } from "@/config/routes";
import { useAssistant } from "@/hooks/useAssistant";
import { useAuth } from "@/hooks/useAuth";
import { useConversation } from "@/hooks/useConversation";

import { AssistantLayoutManager } from "./AssistantLayoutManager";
import { AssistantLauncher } from "./AssistantLauncher";
import { AssistantPanel } from "./AssistantPanel";

export function AssistantHost() {
  const auth = useAuth();
  const { mode, setMode } = useAssistant();
  const conversation = useConversation();
  const navigate = useNavigate();

  const workspace = auth.isAuthenticated ? "dashboard" : "guest";

  async function handleClose(): Promise<void> {
    if (workspace === "guest") {
      setMode("CLOSED");
      navigate(APP_ROUTES.landing, { replace: true });
      return;
    }

    setMode("CLOSED");
  }

  return (
    <AssistantLayoutManager
      workspace={workspace}
      onCreateConversation={conversation.createConversation}
      onCloseGuest={() => void handleClose()}
    >
      {(layout) => (
        <>
          {workspace === "dashboard" ? (
            mode === "CLOSED" ? <AssistantLauncher mode={mode} onActivate={layout.openAssistant} /> : null
          ) : null}

          {workspace === "guest" || mode === "DOCKED" || mode === "FULLSCREEN" ? (
            <AssistantPanel
              workspace={workspace}
              layout={layout}
              conversations={conversation.conversations}
              currentConversation={conversation.currentConversation}
              currentConversationId={conversation.currentConversationId}
              loading={conversation.loading}
              isSending={conversation.isSending}
              error={conversation.error}
              onCreateConversation={conversation.createConversation}
              onSelectConversation={conversation.selectConversation}
              onDeleteConversation={conversation.deleteConversation}
              onSettings={() => {}}
              onClose={() => void handleClose()}
            />
          ) : null}
        </>
      )}
    </AssistantLayoutManager>
  );
}
