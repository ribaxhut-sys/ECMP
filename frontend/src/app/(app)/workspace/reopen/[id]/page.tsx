"use client";

import { use } from "react";
import { useTranslations } from "next-intl";
import { ReopenRoutingWorkspace } from "@/features/reopen-routing";
import { ShellPlaceholderPage } from "@/features/shell";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

/**
 * SCR-WS-03 — Reopen Routing (WF-001-06 / R2-B2, mock only).
 */
export default function ReopenRoutingPage({
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
          { label: t("homeCrumb"), href: "/workspace" },
          { label: t("batchPlaceholder") },
        ]}
      />
    );
  }

  return (
    <PermissionGuard permission={SHELL_PERMISSIONS.workspaceIntake}>
      <ReopenRoutingWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
