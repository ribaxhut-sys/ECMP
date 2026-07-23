"use client";

import type { ReactNode } from "react";
import { AppLayout } from "./AppLayout";
import { RequireAuth } from "./RequireAuth";

export function AuthenticatedShell({ children }: { children: ReactNode }) {
  return (
    <RequireAuth>
      <AppLayout>{children}</AppLayout>
    </RequireAuth>
  );
}
