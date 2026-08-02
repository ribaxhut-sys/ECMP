"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconEmpty } from "@/shared/icons";

export interface EmptyProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description: string;
  action?: ReactNode;
  secondaryAction?: ReactNode;
  icon?: ReactNode;
}

export function Empty({
  className,
  title,
  description,
  action,
  secondaryAction,
  icon,
  ...props
}: EmptyProps) {
  const tCommon = useTranslations("common");

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-[var(--ecmp-radius-card)] border border-dashed border-ecmp-border bg-ecmp-surface-sunken px-4 py-10 text-center",
        className,
      )}
      {...props}
    >
      <div className="flex size-12 items-center justify-center rounded-[var(--ecmp-radius-lg)] bg-ecmp-surface text-ecmp-text-secondary shadow-ecmp-raised">
        {icon ?? <IconEmpty className="size-6" aria-hidden />}
      </div>
      <p className="mt-4 text-[length:var(--ecmp-font-card-title-size)] font-[number:var(--ecmp-font-card-title-weight)] text-ecmp-text-primary">
        {title ?? tCommon("emptyTitle")}
      </p>
      <p className="mt-1 max-w-md text-[length:var(--ecmp-font-body-small-size)] text-ecmp-text-secondary">
        {description}
      </p>
      {action || secondaryAction ? (
        <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
          {action}
          {secondaryAction}
        </div>
      ) : null}
    </div>
  );
}
