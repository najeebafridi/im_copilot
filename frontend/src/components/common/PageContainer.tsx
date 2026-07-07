import { type PropsWithChildren } from "react";

import { THEME } from "@/config/theme";

export function PageContainer({ children }: PropsWithChildren) {
  return (
    <div
      className="mx-auto w-full max-w-6xl px-5 py-6 sm:px-6 lg:px-8"
      style={{
        paddingTop: THEME.spacing.pageY,
        paddingBottom: THEME.spacing.pageY,
      }}
    >
      {children}
    </div>
  );
}
