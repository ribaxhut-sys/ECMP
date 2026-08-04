"use client";

import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import {
  APP_NAV_ITEMS,
  isNavItemVisible,
} from "@/shared/layouts/app-layout/nav";
import { Empty, PageContainer } from "@/shared/ui";

/** Single source of truth: same NavItem Commit 6 gates the sidebar with. */
const COMPLAINTS_NAV_ITEM = APP_NAV_ITEMS.find(
  (item) => item.id === "complaints",
)!;

export default function ComplaintsLayout({
  children,
}: {
  children: ReactNode;
}) {
  const router = useRouter();
  const { hasPermission } = useAuth();
  const t = useTranslations("complaints");
  const tCommon = useTranslations("common");

  if (!isNavItemVisible(COMPLAINTS_NAV_ITEM, hasPermission)) {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <Empty
          title={t("accessRestricted")}
          description={t("moduleAccessDescription")}
          primaryAction={{
            label: tCommon("goHome"),
            onClick: () => router.push("/dashboard"),
          }}
        />
      </PageContainer>
    );
  }

  return <>{children}</>;
}
