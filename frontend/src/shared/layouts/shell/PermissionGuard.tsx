"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { PageContainer } from "@/shared/ui";
import { EmptyWorkspace } from "./EmptyWorkspace";

export interface PermissionGuardProps {
  /** Permission string required (mock shell:* or real catalog). */
  permission?: string;
  /** Any-of permissions. */
  anyOf?: readonly string[];
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Placeholder permission gate — hide/show only; no backend AuthZ.
 */
export function PermissionGuard({
  permission,
  anyOf,
  children,
  fallback,
}: PermissionGuardProps) {
  const { hasPermission } = useAuth();
  const t = useTranslations("common");

  const allowed =
    (!permission && (!anyOf || anyOf.length === 0)) ||
    (permission ? hasPermission(permission) : false) ||
    (anyOf?.some((p) => hasPermission(p)) ?? false);

  if (allowed) return <>{children}</>;

  if (fallback) return <>{fallback}</>;

  return (
    <PageContainer>
      <EmptyWorkspace
        title={t("accessRestricted")}
        description={t("notFoundDescription")}
      />
    </PageContainer>
  );
}
