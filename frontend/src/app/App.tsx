import { AuthProvider } from "@/providers/AuthProvider";
import { AssistantProvider } from "@/providers/AssistantProvider";
import { ConversationProvider } from "@/providers/ConversationProvider";
import { ThemeProvider } from "@/providers/ThemeProvider";
import { AppRoutes } from "@/routes/AppRoutes";
import { BrowserRouter } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <AssistantProvider>
            <ConversationProvider>
              <AppRoutes />
            </ConversationProvider>
          </AssistantProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
}
