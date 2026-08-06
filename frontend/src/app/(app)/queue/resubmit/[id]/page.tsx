"use client";

import { use } from "react";
import { useTranslations } from "next-intl";
import { RejectedResubmissionWorkspace } from "@/features/rejected-resubmission";
import { ShellPlaceholderPage } from "@/features/shell";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { isBatchAtLeast } from "@/shared/config/uiBatch";

/**
 * SCR-WS-06 — Rejected Resubmission (WF-001-09 / R2-B1, mock only).
 * Embedded SCR-HX-01 Decision History is required for continuity.
 */
export default function RejectedResubmissionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const t = useTranslations("shell");

  if (!isBatchAtLeast("R2B1")) {
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
      <RejectedResubmissionWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
