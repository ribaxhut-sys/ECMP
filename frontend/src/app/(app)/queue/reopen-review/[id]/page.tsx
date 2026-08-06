"use client";

import { use } from "react";
import { useTranslations } from "next-intl";
import { ReopenApprovalWorkspace } from "@/features/reopen-approval";
import { ShellPlaceholderPage } from "@/features/shell";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

/**
 * SCR-WS-12 — Reopen Approval (WF-001-17 / R2-B2, mock only).
 */
export default function ReopenApprovalPage({
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
    <PermissionGuard permission={SHELL_PERMISSIONS.queueSupervisor}>
      <ReopenApprovalWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
