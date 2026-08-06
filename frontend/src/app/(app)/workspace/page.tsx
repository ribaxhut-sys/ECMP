"use client";

import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { ShellPlaceholderPage } from "@/features/shell";
import { IntakeWorkspace } from "@/features/intake";
import {
  EmptyWorkspace,
  PermissionGuard,
  WorkspaceLayout,
} from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import {
  getShellBatchOverlineKey,
  isBatchAtLeast,
} from "@/shared/config/uiBatch";
import { PageHeader } from "@/shared/ui";

/**
 * Complaint Workspace entry.
 * B3+ Officer intake → SCR-WS-01 New Intake (mock).
 * Earlier shell batches → placeholder.
 */
export default function WorkspacePage() {
  const t = useTranslations("shell");
  const { mockPersona } = useAuth();
  const overline = t(getShellBatchOverlineKey());

  if (mockPersona === "manager") {
    return (
      <WorkspaceLayout>
        <PageHeader
          overline={overline}
          title={t("managerDeferred")}
          description={t("managerDeferredDescription")}
          breadcrumbs={[
            { label: t("homeCrumb"), href: "/workspace" },
            { label: t("managerDeferred") },
          ]}
        />
        <EmptyWorkspace
          title={t("managerDeferred")}
          description={t("managerDeferredDescription")}
        />
      </WorkspaceLayout>
    );
  }

  if (isBatchAtLeast("B3")) {
    return (
      <PermissionGuard permission={SHELL_PERMISSIONS.workspaceIntake}>
        <IntakeWorkspace />
      </PermissionGuard>
    );
  }

  return (
    <PermissionGuard permission={SHELL_PERMISSIONS.workspaceIntake}>
      <ShellPlaceholderPage
        titleKey="workspace"
        descriptionKey="workspaceDescription"
        breadcrumbs={[
          { label: t("homeCrumb"), href: "/workspace" },
          { label: t("workspace") },
        ]}
      />
    </PermissionGuard>
  );
}
