"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { IconEmpty } from "@/shared/icons";

export interface EmptyProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  description: string;
  action?: ReactNode;
}

export function Empty({
  className,
  title,
  description,
  action,
  ...props
}: EmptyProps) {
  const tCommon = useTranslations("common");

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-[var(--ecmp-radius-lg)] border border-dashed border-ecmp-border px-4 py-10 text-center",
        className,
      )}
      {...props}
    >
      <IconEmpty className="size-8 text-ecmp-text-secondary" />
      <p className="mt-3 text-[length:var(--ecmp-font-subtitle-size)] font-semibold text-ecmp-text-primary">
        {title ?? tCommon("emptyTitle")}
      </p>
      <p className="mt-1 max-w-md text-[length:var(--ecmp-font-body-size)] text-ecmp-text-secondary">
        {description}
      </p>
      {action ? <div className="mt-4">{action}</div> : null}
    </div>
  );
}
