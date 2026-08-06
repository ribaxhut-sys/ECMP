"use client";

import { use } from "react";
import { useTranslations } from "next-intl";
import { ReopenedContinuationWorkspace } from "@/features/reopened-continuation";
import { ShellPlaceholderPage } from "@/features/shell";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

/**
 * SCR-WS-07 — Reopened Continuation (WF-001-10 / R2-B2, mock only).
 */
export default function ReopenedContinuationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const t = useTranslations("shell");

  if (!isBatchAtLeast("R2B2")) {
    return (
      <ShellPlaceholderPage
        titleKey="batchPlaceholder"
        descriptionKey="batchPlaceholderDescription"
        breadcrumbs={[
          { label: t("homeCrumb"), href: "/queue" },
          { label: t("batchPlaceholder") },
        ]}
      />
    );
  }

  return (
    <PermissionGuard permission={SHELL_PERMISSIONS.queueAssigned}>
      <ReopenedContinuationWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
