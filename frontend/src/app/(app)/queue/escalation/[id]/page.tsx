"use client";

import { use } from "react";
import { useTranslations } from "next-intl";
import { EscalationHandlingWorkspace } from "@/features/escalation-handling";
import { ShellPlaceholderPage } from "@/features/shell";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

/**
 * SCR-WS-11 — Escalation Handling (WF-001-16 / R2-B3, mock only).
 */
export default function EscalationHandlingPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const t = useTranslations("shell");

  if (!isBatchAtLeast("R2B3")) {
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
      <EscalationHandlingWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
