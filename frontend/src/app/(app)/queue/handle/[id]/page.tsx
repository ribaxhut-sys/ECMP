"use client";

import { use } from "react";
import { HandlingWorkspace } from "@/features/officer-handle";
import { PermissionGuard } from "@/shared/layouts/shell";
import { SHELL_PERMISSIONS } from "@/auth/mockAuth";

/**
 * SCR-WS-04 — Officer Handling Workspace (WF-001-R1 Batch B2, mock only).
 * Officer-only via PermissionGuard.
 */
export default function HandlingWorkspacePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);

  return (
    <PermissionGuard permission={SHELL_PERMISSIONS.queueAssigned}>
      <HandlingWorkspace complaintId={id} />
    </PermissionGuard>
  );
}
