"use client";

import type { ReactNode } from "react";
import { OrgUnitBranchProvider } from "@/features/announcements/useOrgUnitCode";
import { AppLayout } from "./AppLayout";
import { RequireAuth } from "./RequireAuth";

export function AuthenticatedShell({ children }: { children: ReactNode }) {
  return (
    <RequireAuth>
      <OrgUnitBranchProvider>
        <AppLayout>{children}</AppLayout>
      </OrgUnitBranchProvider>
    </RequireAuth>
  );
}
