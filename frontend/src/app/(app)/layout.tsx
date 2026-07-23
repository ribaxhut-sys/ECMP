import type { ReactNode } from "react";
import { AuthenticatedShell } from "@/shared/layouts/app-layout/AuthenticatedShell";

export default function AppSectionLayout({
  children,
}: {
  children: ReactNode;
}) {
  return <AuthenticatedShell>{children}</AuthenticatedShell>;
}
