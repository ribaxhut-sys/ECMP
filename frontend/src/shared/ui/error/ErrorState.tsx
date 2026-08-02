"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useTranslations } from "next-intl";
import { cn } from "@/shared/utils";
import { Alert } from "@/shared/ui/alert";
import { Button } from "@/shared/ui/button";

export interface ErrorStateProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  message: string;
  code?: string;
  actionLabel?: string;
  onRetry?: () => void;
  secondaryAction?: ReactNode;
  children?: ReactNode;
}

export function ErrorState({
  className,
  title,
  message,
  code,
  actionLabel,
  onRetry,
  secondaryAction,
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
        actions={
          <>
            {onRetry ? (
              <Button variant="outline" size="sm" onClick={onRetry}>
                {actionLabel ?? tCommon("retry")}
              </Button>
            ) : null}
            {secondaryAction}
          </>
        }
      />
    </div>
  );
}
