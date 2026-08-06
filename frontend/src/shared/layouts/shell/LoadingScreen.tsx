"use client";

import { useTranslations } from "next-intl";
import { PageContainer, Skeleton } from "@/shared/ui";

export interface LoadingScreenProps {
  label?: string;
}

/** Full content-area loading placeholder for shell gates. */
export function LoadingScreen({ label }: LoadingScreenProps) {
  const t = useTranslations("session");
  return (
    <PageContainer aria-label={label ?? t("loading")} aria-busy>
      <Skeleton rows={6} />
    </PageContainer>
  );
}
