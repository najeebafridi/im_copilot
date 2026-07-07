import { PagePlaceholder } from "@/components/common/PagePlaceholder";
import { AssistantPlaceholder } from "@/features/chat/AssistantPlaceholder";

export function Admin() {
  return (
    <>
      <PagePlaceholder
        title="Admin"
        description="This placeholder admin page will later host upload, management, and monitoring tools."
      />
      <AssistantPlaceholder />
    </>
  );
}
