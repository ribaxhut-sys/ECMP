"use client";

import { use } from "react";
import { AssignmentWorkspace } from "@/features/supervisor-assign";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";

/**
 * SCR-WS-09 — Assignment Workspace (WF-001-R1 Batch B1, mock only).
 * Supervisor-only via PermissionGuard.
 */
export default function AssignmentWorkspacePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <PermissionGuard permission={SHELL_PERMISSIONS.queueSupervisor}>
      <AssignmentWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
