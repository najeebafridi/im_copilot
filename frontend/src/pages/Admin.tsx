import { PagePlaceholder } from "@/components/common/PagePlaceholder";
import { AssistantPlaceholder } from "@/features/chat/AssistantPlaceholder";

export function Admin() {
  return (
    <>
      <PagePlaceholder
        title="Admin"
        description="Administrator access is handled through the protected application shell."
      />
      <AssistantPlaceholder />
    </>
  );
}
