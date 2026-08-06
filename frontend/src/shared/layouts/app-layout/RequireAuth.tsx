"use client";

import { useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { PageContainer, Skeleton } from "@/shared/ui";

/**
 * Client-side session gate. Preserves existing auth redirect behavior;
 * does not alter login/logout/token flows.
 *
 * Self-service / forced password-change UI is retired (Mode A uses DB passwords
 * as-is until Enterprise SSO unlock).
 */
export function RequireAuth({ children }: { children: ReactNode }) {
  const router = useRouter();
  const { status } = useAuth();
  const t = useTranslations("session");

  useEffect(() => {
    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [status, router]);

  if (status === "loading" || status === "unauthenticated") {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]" aria-label={t("loading")}>
        <Skeleton rows={6} />
      </PageContainer>
    );
  }

  return <>{children}</>;
}
