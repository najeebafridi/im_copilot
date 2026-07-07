import { useAuth } from "@/hooks/useAuth";
import { DashboardPage } from "@/features/dashboard/DashboardPage";
import { AssistantPlaceholder } from "@/features/chat/AssistantPlaceholder";

export function Student() {
  const auth = useAuth();

  return (
    <>
      <DashboardPage name={auth.user?.name ?? "Student"} semester="Semester 6" program="BSc Computer Science" />
      <AssistantPlaceholder />
    </>
  );
}
