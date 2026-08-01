"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { Alert } from "@/shared/ui/alert";

export interface ErrorStateProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  code?: string;
  actionLabel?: string;
  onRetry?: () => void;
  children?: ReactNode;
}

export function ErrorState({
  className,
  title,
  message,
  code,
  actionLabel,
  onRetry,
  children,
  ...props
}: ErrorStateProps) {
  const tCommon = useTranslations("common");

  return (
    <div className={cn("w-full", className)} {...props}>
      <Alert
        tone="danger"
        title={title ?? tCommon("errorTitle")}
        description={
          <>
            <p>
              {message}
              {code ? ` (${code})` : ""}
            </p>
            {children}
          </>
        }
        actionLabel={onRetry ? (actionLabel ?? tCommon("retry")) : undefined}
        onAction={onRetry}
      />
    </div>
  );
}
