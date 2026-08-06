"use client";

import type { ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";

export interface EmptyWorkspaceProps {
  title?: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

/** Placeholder content area for Batch B0 destinations. */
export function EmptyWorkspace({
  title,
  description,
  action,
  className,
}: EmptyWorkspaceProps) {
  const t = useTranslations("shell");

  return (
    <div
      className={cn(
        "flex min-h-[16rem] flex-col items-center justify-center gap-3",
        "rounded-[var(--ecmp-radius-lg)] border border-dashed border-ecmp-border/80",
        "bg-ecmp-surface/60 px-[var(--ecmp-page-gutter)] py-[var(--ecmp-section-gap)] text-center",
        className,
      )}
      role="status"
    >
      <p className="text-[length:var(--ecmp-font-card-title-size)] font-semibold text-ecmp-text-primary">
        {title ?? t("emptyTitle")}
      </p>
      <p className="max-w-md text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        {description ?? t("emptyDescription")}
      </p>
      {action}
    </div>
  );
}
