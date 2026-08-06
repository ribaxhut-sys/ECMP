"use client";

import { useTranslations } from "next-intl";
import {
  EmptyWorkspace,
  WorkspaceLayout,
} from "@/shared/layouts/shell";
import { PageHeader } from "@/shared/ui";
import type { BreadcrumbItem } from "@/shared/ui";

export interface ShellPlaceholderPageProps {
  titleKey:
    | "workspace"
    | "queue"
    | "managerDeferred"
    | "batchPlaceholder";
  descriptionKey:
    | "workspaceDescription"
    | "queueDescription"
    | "queueOfficerDeferredDescription"
    | "managerDeferredDescription"
    | "batchPlaceholderDescription";
  breadcrumbs?: readonly BreadcrumbItem[];
}

/** Reusable B0 destination placeholder (no complaint domain UI). */
export function ShellPlaceholderPage({
  titleKey,
  descriptionKey,
  breadcrumbs,
}: ShellPlaceholderPageProps) {
  const t = useTranslations("shell");

  return (
    <WorkspaceLayout>
      <PageHeader
        overline={t("batchOverline")}
        title={t(titleKey)}
        description={t(descriptionKey)}
        breadcrumbs={breadcrumbs}
      />
      <EmptyWorkspace
        title={t("readyForNextBatch")}
        description={t("readyForNextBatchDescription")}
      />
    </WorkspaceLayout>
  );
}
