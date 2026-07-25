"use client";

import { useEffect } from "react";
import { ErrorState, PageContainer } from "@/shared/ui";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <PageContainer className="space-y-6">
      <ErrorState
        title="Something went wrong"
        message="An unexpected error occurred. You can try again, or navigate back using the sidebar."
        code={error.digest}
        actionLabel="Retry"
        onRetry={reset}
      />
    </PageContainer>
  );
}
