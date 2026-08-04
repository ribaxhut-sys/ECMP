"use client";

import { useEffect } from "react";
import { useTranslations } from "next-intl";
import { ErrorState, PageContainer } from "@/shared/ui";

export default function AppError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  const t = useTranslations("errors");
  const tCommon = useTranslations("common");

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <ErrorState
        title={t("appErrorTitle")}
        message={t("appErrorMessage")}
        actionLabel={tCommon("retry")}
        onRetry={reset}
      />
    </PageContainer>
  );
}
