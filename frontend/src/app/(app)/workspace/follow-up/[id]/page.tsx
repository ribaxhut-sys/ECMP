"use client";

import { use } from "react";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { FollowUpWorkspace } from "@/features/intake";
import { isBatchAtLeast } from "@/shared/config/uiBatch";
import { ShellPlaceholderPage } from "@/features/shell";
import { useTranslations } from "next-intl";

interface FollowUpPageProps {
  params: Promise<{ id: string }>;
}

/** SCR-WS-02 — Follow-up route (Batch B3+). */
export default function FollowUpPage({ params }: FollowUpPageProps) {
  const { id } = use(params);
  const t = useTranslations("shell");

  if (!isBatchAtLeast("B3")) {
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
      <FollowUpWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
