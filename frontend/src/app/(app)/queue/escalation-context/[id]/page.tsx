"use client";

import { use } from "react";
import { useTranslations } from "next-intl";
import { EscalationHandoverWorkspace } from "@/features/escalation-handover";
import { ShellPlaceholderPage } from "@/features/shell";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

/**
 * SCR-WS-08 — Escalation Context Handover (WF-001-11 / R2-B3, mock only).
 */
export default function EscalationHandoverPage({
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
    <PermissionGuard permission={SHELL_PERMISSIONS.queueAssigned}>
      <EscalationHandoverWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
