"use client";

import { Suspense } from "react";
import { useTranslations } from "next-intl";
import { QueueDashboardView } from "@/features/queue";
import { ShellPlaceholderPage } from "@/features/shell";
import { SupervisorQueue } from "@/features/supervisor-assign";
import { OfficerQueue } from "@/features/officer-handle";
import {
  isBatchAtLeast,
  isBatchB0,
  isShellUiBatch,
} from "@/shared/config/uiBatch";
import { useAuth } from "@/auth/AuthProvider";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";
import { PageFallback } from "@/shared/ui";

/**
 * Queue entry (shell batches).
 * B1+ Supervisor → SCR-Q-02 Unassigned (mock).
 * B2+ Officer → SCR-Q-01 Assigned Queue (mock).
 * B0 / earlier → placeholder.
 * Non-shell → API QueueDashboardView.
 */
export default function QueuePage() {
  const t = useTranslations("shell");
  const { isMockSession, hasPermission } = useAuth();
  const shellMode = isShellUiBatch() || isMockSession;

  if (shellMode) {
    if (
      isBatchAtLeast("B1") &&
      hasPermission(SHELL_PERMISSIONS.queueSupervisor)
    ) {
      return (
        <PermissionGuard permission={SHELL_PERMISSIONS.queueSupervisor}>
          <SupervisorQueue />
        </PermissionGuard>
      );
    }

    if (
      isBatchAtLeast("B2") &&
      hasPermission(SHELL_PERMISSIONS.queueAssigned)
    ) {
      return (
        <PermissionGuard permission={SHELL_PERMISSIONS.queueAssigned}>
          <OfficerQueue />
        </PermissionGuard>
      );
    }

    return (
      <PermissionGuard
        anyOf={[
          SHELL_PERMISSIONS.queueAssigned,
          SHELL_PERMISSIONS.queueSupervisor,
        ]}
      >
        <ShellPlaceholderPage
          titleKey="queue"
          descriptionKey={
            isBatchB0() ? "queueDescription" : "queueOfficerDeferredDescription"
          }
          breadcrumbs={[
            { label: t("homeCrumb"), href: "/queue" },
            { label: t("queue") },
          ]}
        />
      </PermissionGuard>
    );
  }

  return (
    <Suspense fallback={<PageFallback titleKey="queue" />}>
      <QueueDashboardView />
    </Suspense>
  );
}
